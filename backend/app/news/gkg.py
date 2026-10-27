"""Lectura de los archivos GKG que GDELT publica cada 15 minutos.

Cada archivo trae todas las noticias que GDELT ha procesado en esa tanda, con su
título original, su idioma y los lugares que mencionan. Se descargan y se leen
en memoria: nunca se escriben en disco.
"""
import html
import io
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import httpx

from app.news.gdelt import Article

BASE_URL = "http://data.gdeltproject.org/gdeltv2"
SLOT = timedelta(minutes=15)
MAX_COUNTRIES = 3

# idiomas que GDELT traduce (ISO 639-3 → ISO 639-1)
LANG3 = {
    "afr": "af", "sqi": "sq", "ara": "ar", "hye": "hy", "aze": "az", "ben": "bn", "bos": "bs",
    "bul": "bg", "cat": "ca", "zho": "zh", "hrv": "hr", "ces": "cs", "dan": "da", "nld": "nl",
    "est": "et", "fin": "fi", "fra": "fr", "glg": "gl", "kat": "ka", "deu": "de", "ell": "el",
    "guj": "gu", "heb": "he", "hin": "hi", "hun": "hu", "isl": "is", "ind": "id", "ita": "it",
    "jpn": "ja", "kan": "kn", "kaz": "kk", "kor": "ko", "lav": "lv", "lit": "lt", "mkd": "mk",
    "msa": "ms", "mal": "ml", "mar": "mr", "mon": "mn", "nep": "ne", "nor": "no", "fas": "fa",
    "pol": "pl", "por": "pt", "pan": "pa", "ron": "ro", "rus": "ru", "srp": "sr", "sin": "si",
    "slk": "sk", "slv": "sl", "som": "so", "spa": "es", "swa": "sw", "swe": "sv", "tam": "ta",
    "tel": "te", "tha": "th", "tur": "tr", "ukr": "uk", "urd": "ur", "vie": "vi", "pus": "ps",
}

TITLE_RE = re.compile(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", re.S)
LANG_RE = re.compile(r"srclc:(\w+)")


def slot_floor(dt: datetime) -> datetime:
    return dt.replace(minute=dt.minute - dt.minute % 15, second=0, microsecond=0)


def file_url(slot: datetime, translation: bool) -> str:
    kind = "translation.gkg" if translation else "gkg"
    return f"{BASE_URL}/{slot:%Y%m%d%H%M%S}.{kind}.csv.zip"


async def fetch_gkg(client: httpx.AsyncClient, url: str) -> str | None:
    """Devuelve el contenido del archivo, o None si GDELT aún no lo ha publicado."""
    r = await client.get(url)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        return z.read(z.namelist()[0]).decode("utf-8", "replace")


def _main_countries(locations: str, fips: dict[str, str]) -> list[tuple[str, int]]:
    # Cada lugar mencionado suma un punto a su país. Cuentan los países con al
    # menos la mitad de puntos que el más mencionado: así se descartan los que
    # solo aparecen de pasada.
    points = Counter()
    for loc in locations.split(";"):
        parts = loc.split("#")
        if len(parts) > 2 and parts[2] in fips:
            points[fips[parts[2]]] += 1
    if not points:
        return []
    top = max(points.values())
    return [(iso3, n) for iso3, n in points.most_common(MAX_COUNTRIES) if n * 2 >= top]


def parse_gkg(
    text: str, fips: dict[str, str], per_country_cap: int = 5
) -> tuple[dict[str, list[Article]], dict[str, int]]:
    articles: dict[str, list[Article]] = defaultdict(list)
    counts: Counter = Counter()
    for line in text.splitlines():
        f = line.split("\t")
        if len(f) < 27:
            continue
        title = TITLE_RE.search(f[26])
        countries = _main_countries(f[9], fips)
        if not title or not title.group(1).strip() or not countries:
            continue
        lang = LANG_RE.match(f[25])
        try:
            seen_at = datetime.strptime(f[1], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
        article = Article(
            url=f[4],
            title=html.unescape(title.group(1)).strip(),
            language=LANG3.get(lang.group(1), "und") if lang else "en",
            domain=f[3],
            source_country="",
            seen_at=seen_at,
        )
        for iso3, score in countries:
            counts[iso3] += 1
            articles[iso3].append(replace(article, score=score))
    # de cada tanda se guardan solo las más relevantes de cada país
    top = {iso3: sorted(items, key=lambda a: -a.score)[:per_country_cap] for iso3, items in articles.items()}
    return top, dict(counts)
