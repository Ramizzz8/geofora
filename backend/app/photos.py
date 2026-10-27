"""Fotos del país desde Wikimedia (libres, con autor y licencia).

Se toman primero de Wikivoyage, cuya portada de cada país muestra paisajes y
ciudades; si hay pocas, se completan con las del artículo de Wikipedia.
"""
import html
import re
import sqlite3
import time
from urllib.parse import quote

import httpx

from app.cache import CacheResult, cached
from app.countries import Country

VOYAGE_URL = "https://en.wikivoyage.org/api/rest_v1/page/media-list"
WIKI_URL = "https://es.wikipedia.org/api/rest_v1/page/media-list"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
TTL_S = 30 * 86400
MAX_PHOTOS = 6
THUMB_WIDTH = 800

# mapas, banderas, escudos y fotos militares no sirven para enseñar el país
EXCLUDE = re.compile(
    r"map|location|locator|flag|bandera|coat|escudo|seal|emblem|visa|aiga|orthographic|"
    r"navy|usmc|army|military|marine|soldier|troops|guard|police|bomb|atomic|"
    r"airport|aircraft|airline|boeing|airbus|fokker",
    re.I,
)
PHOTO_EXT = re.compile(r"\.jpe?g$", re.I)


async def _candidates(client: httpx.AsyncClient, base: str, title: str) -> list[str]:
    r = await client.get(f"{base}/{quote(title.replace(' ', '_'), safe='()_')}")
    if r.status_code == 404:
        return []
    r.raise_for_status()
    out = []
    for item in r.json().get("items", []):
        if item.get("type") != "image":
            continue
        name = item["title"].split(":", 1)[1]
        if PHOTO_EXT.search(name) and not EXCLUDE.search(name):
            out.append(f"File:{name}")
    return out


def _plain(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


async def _describe(client: httpx.AsyncClient, files: list[str]) -> list[dict]:
    r = await client.get(COMMONS_API, params={
        "action": "query", "titles": "|".join(files), "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime", "iiurlwidth": THUMB_WIDTH,
        "format": "json", "formatversion": 2,
    })
    r.raise_for_status()
    by_title = {p["title"]: p for p in r.json()["query"]["pages"]}
    photos = []
    for f in files:  # se respeta el orden de la página, que pone primero las mejores
        info = (by_title.get(f.replace("_", " "), {}).get("imageinfo") or [None])[0]
        if not info or info.get("mime") != "image/jpeg" or not info.get("thumburl"):
            continue
        meta = info.get("extmetadata", {})
        photos.append({
            "thumb": info["thumburl"],
            "page": info["descriptionurl"],
            "author": _plain(meta.get("Artist", {}).get("value", "")) or "Wikimedia Commons",
            "license": meta.get("LicenseShortName", {}).get("value", ""),
        })
    return photos


async def get_photos(conn: sqlite3.Connection, client: httpx.AsyncClient, country: Country, now=time.time) -> CacheResult:
    async def fetch() -> dict:
        files = await _candidates(client, VOYAGE_URL, country.name_en)
        if len(files) < MAX_PHOTOS // 2:
            files += [f for f in await _candidates(client, WIKI_URL, country.name_es) if f not in files]
        files = files[: MAX_PHOTOS * 2]
        photos = await _describe(client, files) if files else []
        return {"photos": photos[:MAX_PHOTOS]}

    return await cached(conn, f"photos:{country.iso3}", TTL_S, fetch, now=now)
