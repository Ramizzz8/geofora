import asyncio
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
DEEPL_TARGETS = {"en": "EN-US"}
TRANSLATE_TIMEOUT_S = 3  # nginx corta a los 30 s: un DeepL lento no puede bloquear las noticias


class Translator(Protocol):
    async def translate(self, texts: list[str], source: str, target: str) -> list[str]: ...


class DeepLTranslator:
    def __init__(self, api_key: str, client: httpx.AsyncClient):
        self.api_key = api_key
        self.client = client

    async def translate(self, texts: list[str], source: str, target: str) -> list[str]:
        # DeepL exige variante regional para traducir al inglés
        body = {"text": texts, "target_lang": DEEPL_TARGETS.get(target, target.upper())}
        if source != "und":
            body["source_lang"] = source.upper()
        r = await self.client.post(DEEPL_URL, json=body, headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"})
        r.raise_for_status()  # 456 = cuota agotada
        return [t["text"] for t in r.json()["translations"]]


def _hash(target: str, text: str) -> str:
    return hashlib.sha256(f"{target}|{text}".encode()).hexdigest()


async def translate_titles(
    conn: sqlite3.Connection,
    translator: Translator | None,
    articles: list[Article],
    target: str = "es",
    timeout_s: float = TRANSLATE_TIMEOUT_S,
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

    async def one(lang: str, items: list[ArticleOut]):
        return await asyncio.wait_for(
            translator.translate([o.title_original for o in items], lang, target), timeout_s
        )

    results = await asyncio.gather(*(one(l, i) for l, i in pending.items()), return_exceptions=True)
    for (lang, items), translated in zip(pending.items(), results):
        if isinstance(translated, BaseException):
            # sin traducción se muestra el original con su idioma, nunca un error
            log.warning("translation failed for %s: %r", lang, translated)
            continue
        for o, text in zip(items, translated):
            o.title, o.translated = text, True
            conn.execute(
                "INSERT OR REPLACE INTO translations (hash, text) VALUES (?, ?)", (_hash(target, o.title_original), text)
            )
        conn.commit()
    return out
