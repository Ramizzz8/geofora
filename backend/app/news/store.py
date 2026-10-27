import sqlite3
from dataclasses import dataclass

from app.news.gdelt import Article

HOUR = 3600
MAX_ARTICLES = 20


@dataclass
class ArticleOut:
    url: str
    title: str
    title_original: str
    language: str
    translated: bool
    domain: str
    seen_at: float

    @classmethod
    def untranslated(cls, a: Article) -> "ArticleOut":
        return cls(a.url, a.title, a.title, a.language, False, a.domain, a.seen_at)


def save_articles(conn: sqlite3.Connection, iso3: str, articles: list[Article]) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO articles (url, iso3, title, language, domain, source_country, seen_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(a.url, iso3, a.title, a.language, a.domain, a.source_country, a.seen_at) for a in articles],
    )
    conn.commit()


def prune(conn: sqlite3.Connection, older_than: float) -> None:
    conn.execute("DELETE FROM articles WHERE seen_at < ?", (older_than,))
    conn.commit()


def _query(conn, iso3: str, since: float, own_country: str) -> list[Article]:
    rows = conn.execute(
        "SELECT url, title, language, domain, source_country, seen_at FROM articles"
        " WHERE iso3 = ? AND seen_at >= ?"
        " ORDER BY (source_country = ?) DESC, seen_at DESC LIMIT ?",
        (iso3, since, own_country, MAX_ARTICLES),
    ).fetchall()
    return [Article(**dict(r)) for r in rows]


def recent_articles(
    conn: sqlite3.Connection, iso3: str, now: float, own_country: str = "", min_count: int = 5
) -> tuple[list[Article], str]:
    recent = _query(conn, iso3, now - 48 * HOUR, own_country)
    if len(recent) >= min_count:
        return recent, "48h"
    return _query(conn, iso3, now - 7 * 24 * HOUR, own_country), "7d"


def heatmap(conn: sqlite3.Connection, now: float) -> dict[str, int]:
    rows = conn.execute(
        "SELECT iso3, COUNT(*) AS n FROM articles WHERE seen_at >= ? GROUP BY iso3",
        (now - 24 * HOUR,),
    ).fetchall()
    return {r["iso3"]: r["n"] for r in rows}


def last_seen(conn: sqlite3.Connection) -> float | None:
    return conn.execute("SELECT MAX(seen_at) FROM articles").fetchone()[0]
