from datetime import datetime, timezone

from app.db import connect, init_db
from app.news.job import ingest
from app.news.store import heatmap, recent_articles

FIPS = {"AF": "AFG"}
NOW = datetime(2026, 10, 27, 16, 20, tzinfo=timezone.utc)


def gkg(url, date):
    f = [""] * 27
    f[1], f[3], f[4], f[9] = date, "x.com", url, "1#Afghanistan#AF#AF#0#0#AF"
    f[26] = f"<PAGE_TITLE>{url}</PAGE_TITLE>"
    return "\t".join(f)


def make_conn(tmp_path):
    c = connect(str(tmp_path / "j.db"))
    init_db(c)
    return c


async def test_backfills_then_only_new_files(tmp_path):
    conn = make_conn(tmp_path)
    fetched = []

    async def fetch(client, url):
        fetched.append(url)
        stamp = url.rsplit("/", 1)[1][:14]
        return gkg(f"https://a/{stamp}/{'t' if 'translation' in url else 'e'}", stamp)

    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: NOW, backfill_slots=2)
    # 2 tandas de atrás + la actual (16:15), en inglés y en traducción
    assert len(fetched) == 6
    fetched.clear()
    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: NOW, backfill_slots=2)
    assert fetched == []
    assert heatmap(conn, NOW.timestamp()) == {"AFG": 6}
    assert len(recent_articles(conn, "AFG", NOW.timestamp())[0]) == 6


async def test_missing_file_is_retried_next_time(tmp_path):
    conn = make_conn(tmp_path)
    available = {"20261027161500.gkg"}

    async def fetch(client, url):
        name = url.rsplit("/", 1)[1]
        if not any(name.startswith(a) for a in available):
            return None  # GDELT aún no lo ha publicado
        return gkg(f"https://a/{name}", name[:14])

    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: NOW, backfill_slots=0)
    assert heatmap(conn, NOW.timestamp()) == {"AFG": 1}
    available.add("20261027161500.translation")
    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: NOW, backfill_slots=0)
    assert heatmap(conn, NOW.timestamp()) == {"AFG": 2}


async def test_download_error_does_not_advance_cursor(tmp_path):
    conn = make_conn(tmp_path)
    calls = []

    async def fetch(client, url):
        calls.append(url)
        if len(calls) == 1:
            raise TimeoutError()
        return gkg(f"https://a/{len(calls)}", "20261027161500")

    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: NOW, backfill_slots=0)
    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: NOW, backfill_slots=0)
    assert heatmap(conn, NOW.timestamp()) == {"AFG": 2}


async def test_file_missing_for_hours_is_skipped(tmp_path):
    conn = make_conn(tmp_path)

    async def fetch(client, url):
        name = url.rsplit("/", 1)[1]
        if name.startswith("20261027120000"):
            return None  # hueco en GDELT: nunca se publicará
        return gkg(f"https://a/{name}", name[:14])

    late = datetime(2026, 10, 27, 16, 20, tzinfo=timezone.utc)
    await ingest(conn, None, FIPS, fetch=fetch, now=lambda: late, backfill_slots=17, max_files=40)
    # 12:00 se salta y se procesan las 17 tandas siguientes de cada flujo
    assert heatmap(conn, late.timestamp()) == {"AFG": 34}
