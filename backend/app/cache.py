import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from typing import Awaitable, Callable

log = logging.getLogger(__name__)


@dataclass
class CacheResult:
    value: dict
    fetched_at: float
    stale: bool

    def to_response(self) -> dict:
        return {**self.value, "fetched_at": self.fetched_at, "stale": self.stale}


async def cached(
    conn: sqlite3.Connection,
    key: str,
    ttl_s: float,
    fetch: Callable[[], Awaitable[dict]],
    now: Callable[[], float] = time.time,
) -> CacheResult:
    row = conn.execute("SELECT value, fetched_at FROM cache WHERE key = ?", (key,)).fetchone()
    if row and now() - row["fetched_at"] < ttl_s:
        return CacheResult(json.loads(row["value"]), row["fetched_at"], stale=False)
    try:
        value = await fetch()
    except Exception:
        if row is None:
            raise
        # mejor un dato antiguo etiquetado con su fecha que un apartado vacío
        log.warning("fetch failed for %s, serving stale cache", key, exc_info=True)
        return CacheResult(json.loads(row["value"]), row["fetched_at"], stale=True)
    fetched_at = now()
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, value, fetched_at) VALUES (?, ?, ?)",
        (key, json.dumps(value, ensure_ascii=False), fetched_at),
    )
    conn.commit()
    return CacheResult(value, fetched_at, stale=False)
