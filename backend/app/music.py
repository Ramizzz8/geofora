import asyncio
import logging
import sqlite3
import time

import httpx

from app.cache import CacheResult, cached
from app.countries import Country
from app.slug import slugify

log = logging.getLogger(__name__)

LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"
MB_URL = "https://musicbrainz.org/ws/2/artist"
DEEZER_URL = "https://api.deezer.com/search"
DEEZER_TRACK_URL = "https://api.deezer.com/track"
TTL_S = 5 * 86400
LIMIT = 10


async def _chart(client: httpx.AsyncClient, country: Country, api_key: str) -> list[dict]:
    try:
        r = await client.get(LASTFM_URL, params={
            "method": "geo.gettoptracks", "country": country.name_en,
            "api_key": api_key, "format": "json", "limit": LIMIT,
        })
        data = r.json()
        if "error" in data:  # p. ej. 6 = país no reconocido por Last.fm
            return []
        r.raise_for_status()
    except (httpx.HTTPError, ValueError) as e:
        # la excepción original lleva la URL con la clave: no se encadena para que no llegue a los logs
        status = getattr(getattr(e, "response", None), "status_code", None)
        raise RuntimeError(f"Last.fm no disponible ({type(e).__name__}, HTTP {status})") from None
    return [
        {"title": t["name"], "artist": t["artist"]["name"], "deezer_id": None, "link": t["url"],
         "listeners": int(t["listeners"]) if str(t.get("listeners", "")).isdigit() else None, "image": None}
        for t in data.get("tracks", {}).get("track", [])[:LIMIT]
    ]


async def _artists(client: httpx.AsyncClient, country: Country) -> list[dict]:
    r = await client.get(MB_URL, params={"query": f'area:"{country.name_en}"', "limit": LIMIT, "fmt": "json"})
    r.raise_for_status()
    return [
        {"title": None, "artist": a["name"], "deezer_id": None, "listeners": None, "image": None,
         "link": f"https://musicbrainz.org/artist/{a['id']}"}
        for a in r.json().get("artists", [])
    ]


def _same_artist(a: str, b: str) -> bool:
    a, b = slugify(a), slugify(b)
    return bool(a and b) and (a in b or b in a)


async def _add_preview(client: httpx.AsyncClient, item: dict) -> None:
    # La búsqueda estricta artist:"…" track:"…" de Deezer ya no devuelve resultados: se busca
    # en texto libre y se comprueba que el artista coincide.
    q = f'{item["artist"]} {item["title"]}' if item["title"] else item["artist"]
    try:
        r = await client.get(DEEZER_URL, params={"q": q, "limit": 1})
        r.raise_for_status()
        hits = r.json().get("data", [])
    except (httpx.HTTPError, ValueError):
        return  # sin preview la canción sigue apareciendo con su enlace
    # el enlace del fragmento caduca en ~1 h: se guarda el id y el enlace se pide al reproducir
    if hits and not _same_artist(hits[0].get("artist", {}).get("name", ""), item["artist"]):
        return
    if hits and hits[0].get("preview"):
        hit = hits[0]
        # canción: portada del disco; artista sin canción concreta: su foto
        item["image"] = ((hit.get("album") or {}).get("cover_medium") if item["title"]
                         else (hit.get("artist") or {}).get("picture_medium")) or None
        item["deezer_id"] = hit.get("id")
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

    # music3: las entradas antiguas no tenían imagen ni oyentes (y las music1, enlaces caducados)
    return await cached(conn, f"music3:{country.iso3}", TTL_S, fetch, now=now)


async def fresh_preview(client: httpx.AsyncClient, deezer_id: int) -> str | None:
    r = await client.get(f"{DEEZER_TRACK_URL}/{deezer_id}")
    r.raise_for_status()
    return r.json().get("preview") or None
