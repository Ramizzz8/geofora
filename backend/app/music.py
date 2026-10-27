import asyncio
import logging
import sqlite3
import time

import httpx

from app.cache import CacheResult, cached
from app.countries import Country

log = logging.getLogger(__name__)

LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"
MB_URL = "https://musicbrainz.org/ws/2/artist"
DEEZER_URL = "https://api.deezer.com/search"
TTL_S = 5 * 86400
LIMIT = 10


async def _chart(client: httpx.AsyncClient, country: Country, api_key: str) -> list[dict]:
    r = await client.get(LASTFM_URL, params={
        "method": "geo.gettoptracks", "country": country.name_en,
        "api_key": api_key, "format": "json", "limit": LIMIT,
    })
    data = r.json()
    if "error" in data:  # p. ej. 6 = país no reconocido por Last.fm
        return []
    r.raise_for_status()
    return [
        {"title": t["name"], "artist": t["artist"]["name"], "preview_url": None, "link": t["url"]}
        for t in data.get("tracks", {}).get("track", [])[:LIMIT]
    ]


async def _artists(client: httpx.AsyncClient, country: Country) -> list[dict]:
    r = await client.get(MB_URL, params={"query": f'area:"{country.name_en}"', "limit": LIMIT, "fmt": "json"})
    r.raise_for_status()
    return [
        {"title": None, "artist": a["name"], "preview_url": None, "link": f"https://musicbrainz.org/artist/{a['id']}"}
        for a in r.json().get("artists", [])
    ]


async def _add_preview(client: httpx.AsyncClient, item: dict) -> None:
    q = f'artist:"{item["artist"]}"' + (f' track:"{item["title"]}"' if item["title"] else "")
    try:
        r = await client.get(DEEZER_URL, params={"q": q, "limit": 1})
        r.raise_for_status()
        hits = r.json().get("data", [])
    except (httpx.HTTPError, ValueError):
        return  # sin preview la canción sigue apareciendo con su enlace
    if hits:
        item["preview_url"] = hits[0].get("preview") or None
        item["link"] = hits[0].get("link") or item["link"]


async def get_music(
    conn: sqlite3.Connection, client: httpx.AsyncClient, country: Country, api_key: str, now=time.time
) -> CacheResult:
    async def fetch() -> dict:
        items = await _chart(client, country, api_key) if api_key else []
        source = "chart"
        if not items:
            items, source = await _artists(client, country), "artists"
        if not items:
            return {"source": "none", "items": []}
        await asyncio.gather(*(_add_preview(client, i) for i in items))
        return {"source": source, "items": items}

    return await cached(conn, f"music:{country.iso3}", TTL_S, fetch, now=now)
