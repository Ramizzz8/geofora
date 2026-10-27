import hashlib
import logging
import sqlite3
from collections import defaultdict
from typing import Protocol

import httpx

from app.news.gdelt import Article
from app.news.store import ArticleOut

log = logging.getLogger(__name__)

DEEPL_URL = "https://api-free.deepl.com/v2/translate"


class Translator(Protocol):
    async def translate(self, texts: list[str], source: str, target: str) -> list[str]: ...


class DeepLTranslator:
    def __init__(self, api_key: str, client: httpx.AsyncClient):
        self.api_key = api_key
        self.client = client

    async def translate(self, texts: list[str], source: str, target: str) -> list[str]:
        body = {"text": texts, "target_lang": target.upper()}
        if source != "und":
            body["source_lang"] = source.upper()
        r = await self.client.post(DEEPL_URL, json=body, headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"})
        r.raise_for_status()  # 456 = cuota agotada
        return [t["text"] for t in r.json()["translations"]]


def _hash(target: str, text: str) -> str:
    return hashlib.sha256(f"{target}|{text}".encode()).hexdigest()


async def translate_titles(
    conn: sqlite3.Connection, translator: Translator | None, articles: list[Article], target: str = "es"
) -> list[ArticleOut]:
    out = [ArticleOut.untranslated(a) for a in articles]
    pending: dict[str, list[ArticleOut]] = defaultdict(list)
    for o in out:
        if o.language == target:
            continue
        row = conn.execute("SELECT text FROM translations WHERE hash = ?", (_hash(target, o.title_original),)).fetchone()
        if row:
            o.title, o.translated = row["text"], True
        elif translator:
            pending[o.language].append(o)

    for lang, items in pending.items():
        try:
            translated = await translator.translate([o.title_original for o in items], lang, target)
        except Exception:
            # sin traducción se muestra el original con su idioma, nunca un error
            log.warning("translation failed for %s", lang, exc_info=True)
            continue
        for o, text in zip(items, translated):
            o.title, o.translated = text, True
            conn.execute(
                "INSERT OR REPLACE INTO translations (hash, text) VALUES (?, ?)", (_hash(target, o.title_original), text)
            )
        conn.commit()
    return out
