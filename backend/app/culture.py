import sqlite3
import time
from urllib.parse import quote

import httpx

from app.cache import CacheResult, cached
from app.countries import Country

SUMMARY_URL = "https://es.wikipedia.org/api/rest_v1/page/summary"
TTL_S = 21 * 86400

# por idioma: URL de Wikipedia, título de respaldo si hay desambiguación y artículo de cultura
WIKIS = {
    "es": (SUMMARY_URL, "{} (país)", "Cultura de {}"),
    "en": ("https://en.wikipedia.org/api/rest_v1/page/summary", "{} (country)", "Culture of {}"),
}


async def _summary(client: httpx.AsyncClient, base: str, title: str) -> dict | None:
    r = await client.get(f"{base}/{quote(title.replace(' ', '_'), safe='()_')}")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


async def get_culture(
    conn: sqlite3.Connection, client: httpx.AsyncClient, country: Country, now=time.time, lang: str = "es"
) -> CacheResult:
    base, fallback, culture_title = WIKIS[lang]
    name = country.name_en if lang == "en" else country.name_es

    async def fetch() -> dict:
        page = await _summary(client, base, name)
        # nombres como "Georgia" llevan a una página de desambiguación
        if page is None or page.get("type") == "disambiguation":
            page = await _summary(client, base, fallback.format(name))
        if page is None:
            raise LookupError(f"no Wikipedia page for {name}")
        culture = await _summary(client, base, culture_title.format(name))
        return {
            "extract": page.get("extract", ""),
            "thumbnail": (page.get("thumbnail") or {}).get("source"),
            "page_url": page["content_urls"]["desktop"]["page"],
            "culture_url": culture["content_urls"]["desktop"]["page"] if culture else None,
        }

    return await cached(conn, f"culture:{lang}:{country.iso3}", TTL_S, fetch, now=now)
