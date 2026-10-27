import sqlite3
import time
from urllib.parse import quote

import httpx

from app.cache import CacheResult, cached
from app.countries import Country

SUMMARY_URL = "https://es.wikipedia.org/api/rest_v1/page/summary"
TTL_S = 21 * 86400


async def _summary(client: httpx.AsyncClient, title: str) -> dict | None:
    r = await client.get(f"{SUMMARY_URL}/{quote(title.replace(' ', '_'), safe='()_')}")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


async def get_culture(
    conn: sqlite3.Connection, client: httpx.AsyncClient, country: Country, now=time.time
) -> CacheResult:
    async def fetch() -> dict:
        page = await _summary(client, country.name_es)
        # nombres como "Georgia" llevan a una página de desambiguación
        if page is None or page.get("type") == "disambiguation":
            page = await _summary(client, f"{country.name_es} (país)")
        if page is None:
            raise LookupError(f"no Wikipedia page for {country.name_es}")
        culture = await _summary(client, f"Cultura de {country.name_es}")
        return {
            "extract": page.get("extract", ""),
            "thumbnail": (page.get("thumbnail") or {}).get("source"),
            "page_url": page["content_urls"]["desktop"]["page"],
            "culture_url": culture["content_urls"]["desktop"]["page"] if culture else None,
        }

    return await cached(conn, f"culture:{country.iso3}", TTL_S, fetch, now=now)
