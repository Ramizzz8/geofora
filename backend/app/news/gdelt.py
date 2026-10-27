from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

from app.countries import Country

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# GDELT devuelve el idioma por su nombre en inglés
LANG_CODES = {
    "Afrikaans": "af", "Albanian": "sq", "Arabic": "ar", "Armenian": "hy", "Azerbaijani": "az",
    "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca", "Chinese": "zh",
    "Croatian": "hr", "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en",
    "Estonian": "et", "Finnish": "fi", "French": "fr", "Galician": "gl", "Georgian": "ka",
    "German": "de", "Greek": "el", "Hebrew": "he", "Hindi": "hi", "Hungarian": "hu",
    "Icelandic": "is", "Indonesian": "id", "Italian": "it", "Japanese": "ja", "Kazakh": "kk",
    "Korean": "ko", "Latvian": "lv", "Lithuanian": "lt", "Macedonian": "mk", "Malay": "ms",
    "Nepali": "ne", "Norwegian": "no", "Pashto": "ps", "Persian": "fa", "Polish": "pl",
    "Portuguese": "pt", "Romanian": "ro", "Russian": "ru", "Serbian": "sr", "Slovak": "sk",
    "Slovenian": "sl", "Somali": "so", "Spanish": "es", "Swahili": "sw", "Swedish": "sv",
    "Tamil": "ta", "Thai": "th", "Turkish": "tr", "Ukrainian": "uk", "Urdu": "ur",
    "Uzbek": "uz", "Vietnamese": "vi",
}


@dataclass
class Article:
    url: str
    title: str
    language: str
    domain: str
    source_country: str
    seen_at: float


def _parse_seendate(s: str) -> float:
    return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).timestamp()


def _norm_title(t: str) -> str:
    return " ".join(t.lower().split())


async def fetch_country_news(client: httpx.AsyncClient, country: Country) -> list[Article]:
    r = await client.get(GDELT_URL, params={
        "query": f'"{country.name_en}"',
        "mode": "artlist",
        "format": "json",
        "maxrecords": 75,
        "timespan": "7d",
        "sort": "datedesc",
    })
    r.raise_for_status()
    try:
        data = r.json()
    except ValueError as e:
        # límite de peticiones o error: GDELT responde 200 con texto plano
        raise ValueError(f"GDELT non-JSON response: {r.text[:100]}") from e

    articles, seen_urls, seen_titles = [], set(), set()
    for a in data.get("articles", []):
        title = (a.get("title") or "").strip()
        key = _norm_title(title)
        if not title or a["url"] in seen_urls or key in seen_titles:
            continue
        seen_urls.add(a["url"])
        seen_titles.add(key)
        articles.append(Article(
            url=a["url"],
            title=title,
            language=LANG_CODES.get(a.get("language", ""), "und"),
            domain=a.get("domain", ""),
            source_country=a.get("sourcecountry", ""),
            seen_at=_parse_seendate(a["seendate"]),
        ))
    return articles
