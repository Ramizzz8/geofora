import asyncio
import logging
import sqlite3
import time
from typing import Iterable

from app.countries import Country
from app.news.gdelt import GDELT_DELAY_S, fetch_country_news
from app.news.store import HOUR, prune, save_articles

log = logging.getLogger(__name__)


async def run_news_cycle(
    conn: sqlite3.Connection,
    client,
    countries: Iterable[Country],
    sleep=asyncio.sleep,
    fetch=fetch_country_news,
    now=time.time,
) -> None:
    ok = failed = 0
    for i, country in enumerate(countries):
        if i:
            await sleep(GDELT_DELAY_S)
        try:
            save_articles(conn, country.iso3, await fetch(client, country))
            ok += 1
        except Exception:
            failed += 1
            log.warning("news fetch failed for %s", country.iso3, exc_info=True)
    prune(conn, now() - 7 * 24 * HOUR)
    log.info("news cycle done: %d ok, %d failed", ok, failed)


async def run_forever(cycle, interval_s: float, sleep=asyncio.sleep, now=time.monotonic, iterations=None) -> None:
    """Repite cycle() cada interval_s contando desde su inicio: si un ciclo tarda más
    que el intervalo, el siguiente empieza en seguida en vez de saltarse una vuelta."""
    i = 0
    while iterations is None or i < iterations:
        start = now()
        try:
            await cycle()
        except Exception:
            log.exception("news cycle crashed")
        elapsed = now() - start
        log.info("news cycle took %.0f s", elapsed)
        await sleep(max(0, interval_s - elapsed))
        i += 1
