import pytest

from app.countries import Country
from app.db import connect, init_db
from app.news.gdelt import Article
from app.news.job import run_news_cycle
from app.news.store import recent_articles

NOW = 1_800_000_000.0


def country(iso3, name):
    return Country(iso3, iso3[:2], name.lower(), name, name, None, [], [], None, [], None)


async def test_cycle_continues_after_country_error(tmp_path):
    conn = connect(str(tmp_path / "j.db"))
    init_db(conn)
    countries = [country("AAA", "Aland"), country("BBB", "Boland"), country("CCC", "Coland")]
    sleeps = []

    async def fake_sleep(s):
        sleeps.append(s)

    async def fake_fetch(client, c):
        if c.iso3 == "BBB":
            raise ValueError("rate limited")
        return [Article(f"https://x/{c.iso3}", c.name_en, "en", "x", "", NOW - 60)]

    await run_news_cycle(conn, None, countries, sleep=fake_sleep, fetch=fake_fetch, now=lambda: NOW)

    assert len(recent_articles(conn, "AAA", NOW)[0]) == 1
    assert len(recent_articles(conn, "BBB", NOW)[0]) == 0
    assert len(recent_articles(conn, "CCC", NOW)[0]) == 1
    assert sleeps and set(sleeps) == {5}
