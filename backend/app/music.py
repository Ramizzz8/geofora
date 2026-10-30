import asyncio
import logging
import sqlite3
import time

import httpx

from app.cache import CacheResult, cached
from app.countries import Country
from app.slug import slugify

log = logging.getLogger(__name__)

APPLE_URL = "https://rss.marketingtools.apple.com/api/v2"
MB_URL = "https://musicbrainz.org/ws/2/artist"
DEEZER_URL = "https://api.deezer.com/search"
DEEZER_TRACK_URL = "https://api.deezer.com/track"
TTL_S = 86400  # el ranking cambia a diario
LIMIT = 10
APPLE_ATTEMPTS = 3
APPLE_TIMEOUT_S = 6
APPLE_RETRY_DELAY_S = 0.5


async def _chart(client: httpx.AsyncClient, country: Country, sleep) -> list[dict]:
    """Lo más escuchado en Apple Music en ese país. Su servicio falla a menudo al azar y da
    error 500 en los países que no tiene, sin distinción: tras varios intentos se da por vacío."""
    url = f"{APPLE_URL}/{country.iso2.lower()}/music/most-played/{LIMIT}/songs.json"
    for attempt in range(APPLE_ATTEMPTS):
        if attempt:
            await sleep(APPLE_RETRY_DELAY_S)
        try:
            r = await client.get(url, timeout=APPLE_TIMEOUT_S)
            r.raise_for_status()
            results = r.json()["feed"]["results"]
        except (httpx.HTTPError, ValueError, KeyError) as e:
            log.info("apple music %s, intento %d: %r", country.iso3, attempt + 1, e)
            continue
        return [
            {"title": t["name"], "artist": t["artistName"], "deezer_id": None, "link": t["url"],
             "image": t["artworkUrl100"].replace("100x100", "200x200")}
            for t in results[:LIMIT]
        ]
    return []


async def _artists(client: httpx.AsyncClient, country: Country) -> list[dict]:
    r = await client.get(MB_URL, params={"query": f'area:"{country.name_en}"', "limit": LIMIT, "fmt": "json"})
    r.raise_for_status()
    return [
        {"title": None, "artist": a["name"], "deezer_id": None, "image": None,
         "link": f"https://musicbrainz.org/artist/{a['id']}"}
        for a in r.json().get("artists", [])
    ]


def _same_artist(a: str, b: str) -> bool:
    a, b = slugify(a), slugify(b)
    return bool(a and b) and (a in b or b in a)


async def _add_preview(client: httpx.AsyncClient, item: dict) -> None:
    # La búsqueda estricta artist:"…" track:"…" de Deezer ya no devuelve resultados: se busca
    # en texto libre y se comprueba que el artista coincide. Apple lista a todos los artistas
    # («Feid, El America»): basta con el principal.
    artist = item["artist"].split(",")[0].split(" & ")[0].strip()
    q = f'{artist} {item["title"]}' if item["title"] else artist
    try:
        r = await client.get(DEEZER_URL, params={"q": q, "limit": 1})
        r.raise_for_status()
        hits = r.json().get("data", [])
    except (httpx.HTTPError, ValueError):
        return  # sin preview la canción sigue apareciendo con su enlace
    if not hits or not hits[0].get("preview") or not _same_artist(hits[0].get("artist", {}).get("name", ""), artist):
        return
    hit = hits[0]
    # el enlace del fragmento caduca en ~1 h: se guarda el id y el enlace se pide al reproducir
    item["deezer_id"] = hit.get("id")
    if not item["title"]:  # artista sin canción concreta: su foto; el ranking ya trae portada y enlace de Apple
        item["image"] = (hit.get("artist") or {}).get("picture_medium") or None
        item["link"] = hit.get("link") or item["link"]


async def get_music(
    conn: sqlite3.Connection, client: httpx.AsyncClient, country: Country, now=time.time, sleep=asyncio.sleep
) -> CacheResult:
    async def fetch() -> dict:
        items = await _chart(client, country, sleep)
        source = "chart"
        if not items:
            items, source = await _artists(client, country), "artists"
        if not items:
            return {"source": "none", "items": []}
        await asyncio.gather(*(_add_preview(client, i) for i in items))
        return {"source": source, "items": items}

    # music4: las entradas anteriores venían de Last.fm
    return await cached(conn, f"music4:{country.iso3}", TTL_S, fetch, now=now)


async def fresh_preview(client: httpx.AsyncClient, deezer_id: int) -> str | None:
    r = await client.get(f"{DEEZER_TRACK_URL}/{deezer_id}")
    r.raise_for_status()
    return r.json().get("preview") or None
