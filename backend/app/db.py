import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    fetched_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS articles (
    url TEXT NOT NULL,
    iso3 TEXT NOT NULL,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    domain TEXT NOT NULL,
    source_country TEXT NOT NULL,
    seen_at REAL NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    -- una misma noticia puede hablar de varios países y cuenta para cada uno
    PRIMARY KEY (url, iso3)
);
CREATE INDEX IF NOT EXISTS idx_articles_iso3_seen ON articles (iso3, seen_at);
-- noticias por país en cada tanda de 15 min de GDELT (para el mapa de calor)
CREATE TABLE IF NOT EXISTS article_counts (
    iso3 TEXT NOT NULL,
    slot REAL NOT NULL,
    stream TEXT NOT NULL,
    n INTEGER NOT NULL,
    PRIMARY KEY (iso3, slot, stream)
);
CREATE TABLE IF NOT EXISTS translations (
    hash TEXT PRIMARY KEY,
    text TEXT NOT NULL
);
"""


def connect(path: str) -> sqlite3.Connection:
    # check_same_thread=False: la conexión la comparten el scheduler y los endpoints
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cols = list(conn.execute("PRAGMA table_info(articles)"))
    if cols and ([c["name"] for c in cols if c["pk"]] == ["url"] or "score" not in {c["name"] for c in cols}):
        # esquema antiguo; es una caché de 7 días, se recrea
        conn.execute("DROP TABLE articles")
    conn.executescript(SCHEMA)
    conn.commit()
