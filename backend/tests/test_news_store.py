import pytest

from app.db import connect, init_db
from app.news.gdelt import Article
from app.news.store import heatmap, prune, recent_articles, save_articles, save_counts

NOW = 1_800_000_000.0
H = 3600


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "n.db"))
    init_db(c)
    return c


def art(i, age_h, country="Spain", lang="es"):
    return Article(f"https://x/{i}", f"titular {i}", lang, "x.com", country, NOW - age_h * H)


def test_widens_to_7d_when_few_recent(conn):
    save_articles(conn, "AFG", [art(i, 10) for i in range(3)] + [art(100 + i, 5 * 24) for i in range(10)])
    arts, rng = recent_articles(conn, "AFG", NOW)
    assert rng == "7d"
    assert len(arts) == 13


def test_keeps_48h_when_enough(conn):
    save_articles(conn, "AFG", [art(i, 10) for i in range(6)] + [art(100 + i, 5 * 24) for i in range(10)])
    arts, rng = recent_articles(conn, "AFG", NOW)
    assert rng == "48h"
    assert len(arts) == 6


def test_caps_at_20_and_most_relevant_first(conn):
    from dataclasses import replace
    save_articles(conn, "AFG", [art(i, 1 + i * 0.1) for i in range(30)] + [replace(art(999, 40), score=5)])
    arts, _ = recent_articles(conn, "AFG", NOW)
    assert len(arts) == 20
    assert arts[0].url == "https://x/999"
    assert arts[1].url == "https://x/0"


def test_upsert_by_url(conn):
    save_articles(conn, "AFG", [art(1, 1)])
    save_articles(conn, "AFG", [art(1, 1)])
    assert len(recent_articles(conn, "AFG", NOW)[0]) == 1


def test_heatmap_sums_counts_of_last_24h(conn):
    save_counts(conn, NOW - 2 * H, "en", {"AFG": 3, "JPN": 1})
    save_counts(conn, NOW - 2 * H, "tr", {"JPN": 4})
    save_counts(conn, NOW - 30 * H, "en", {"AFG": 9})
    assert heatmap(conn, NOW) == {"AFG": 3, "JPN": 5}


def test_prune_removes_old(conn):
    save_articles(conn, "AFG", [art(1, 1), art(2, 8 * 24)])
    prune(conn, NOW - 7 * 24 * H)
    assert [a.url for a in recent_articles(conn, "AFG", NOW + 0)[0]] == ["https://x/1"]


def test_same_url_stored_for_each_country(conn):
    a = art(1, 1)
    save_articles(conn, "FRA", [a])
    save_articles(conn, "DEU", [a])
    assert len(recent_articles(conn, "FRA", NOW)[0]) == 1
    assert len(recent_articles(conn, "DEU", NOW)[0]) == 1


def test_same_title_from_different_urls_shown_once(conn):
    from dataclasses import replace
    a = art(1, 1)
    save_articles(conn, "AFG", [a, replace(a, url="https://mirror/1", title="Titular  1")] + [art(i, 2) for i in range(2, 8)])
    arts, _ = recent_articles(conn, "AFG", NOW)
    assert [x.url for x in arts].count("https://mirror/1") + [x.url for x in arts].count("https://x/1") == 1
    assert len(arts) == 7
