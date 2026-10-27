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
    -- una misma noticia puede hablar de varios países y cuenta para cada uno
    PRIMARY KEY (url, iso3)
);
CREATE INDEX IF NOT EXISTS idx_articles_iso3_seen ON articles (iso3, seen_at);
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
    pk = [r["name"] for r in conn.execute("PRAGMA table_info(articles)") if r["pk"]]
    if pk == ["url"]:
        # esquema antiguo con la URL como única clave; es una caché de 7 días, se recrea
        conn.execute("DROP TABLE articles")
    conn.executescript(SCHEMA)
    conn.commit()
