import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta, timezone

from app.news.gkg import SLOT, fetch_gkg, file_url, parse_gkg, slot_floor
from app.news.store import HOUR, prune, save_articles, save_counts

log = logging.getLogger(__name__)

STREAMS = {"en": False, "tr": True}  # noticias en inglés / traducidas de otros idiomas
GIVE_UP_AFTER = timedelta(hours=3)  # un archivo que no aparece en 3 h no se publicará


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_cursor(conn: sqlite3.Connection, stream: str) -> datetime | None:
    row = conn.execute("SELECT value FROM cache WHERE key = ?", (f"gkg_cursor:{stream}",)).fetchone()
    return datetime.fromisoformat(json.loads(row["value"])["slot"]) if row else None


def _set_cursor(conn: sqlite3.Connection, stream: str, slot: datetime) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, value, fetched_at) VALUES (?, ?, ?)",
        (f"gkg_cursor:{stream}", json.dumps({"slot": slot.isoformat()}), time.time()),
    )
    conn.commit()


async def ingest(
    conn: sqlite3.Connection,
    client,
    fips: dict[str, str],
    fetch=fetch_gkg,
    now=_now,
    backfill_slots: int = 8,
    max_files: int = 12,
) -> None:
    """Procesa las tandas de 15 min publicadas desde la última vez (y, la primera vez,
    las de las últimas 2 h). Cada archivo se lee en memoria y se descarta."""
    current = now()
    latest = slot_floor(current)
    for stream, translation in STREAMS.items():
        cursor = _get_cursor(conn, stream) or latest - SLOT * (backfill_slots + 1)
        slot, done = cursor + SLOT, 0
        while slot <= latest and done < max_files:
            try:
                text = await fetch(client, file_url(slot, translation))
            except Exception:
                log.warning("gkg download failed for %s %s", stream, slot, exc_info=True)
                break
            if text is None:
                if current - slot < GIVE_UP_AFTER:
                    break  # aún no publicado: se reintenta en la próxima vuelta
                log.warning("gkg %s %s never published, skipping", stream, slot)
            else:
                articles, counts = parse_gkg(text, fips)
                for iso3, items in articles.items():
                    save_articles(conn, iso3, items)
                save_counts(conn, slot.timestamp(), stream, counts)
                log.info("gkg %s %s: %d countries, %d articles", stream, slot, len(counts), sum(counts.values()))
            _set_cursor(conn, stream, slot)
            slot += SLOT
            done += 1
    prune(conn, current.timestamp() - 7 * 24 * HOUR)


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
