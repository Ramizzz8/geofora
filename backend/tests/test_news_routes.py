import time

from app.news.gdelt import Article
from app.news.store import save_articles, save_counts


def test_news_empty_country_returns_empty_list(client):
    r = client.get("/api/country/tuvalu/news")
    assert r.status_code == 200
    assert r.json()["articles"] == []


def test_news_returns_articles(client):
    now = time.time()
    save_articles(client.app.state.db, "JPN", [Article("https://x/1", "Tokyo news", "en", "x.com", "Japan", now - 60)])
    body = client.get("/api/country/japon/news").json()
    assert body["range"] == "7d"
    a = body["articles"][0]
    assert a["title_original"] == "Tokyo news"
    assert a["domain"] == "x.com"
    assert set(a) >= {"url", "title", "title_original", "language", "translated", "domain", "seen_at"}


def test_news_unknown_country_404(client):
    assert client.get("/api/country/narnia/news").status_code == 404


def test_heatmap(client):
    now = time.time()
    save_counts(client.app.state.db, now - 60, "en", {"JPN": 1})
    body = client.get("/api/heatmap").json()
    assert body["counts"] == {"JPN": 1}
    assert "updated_at" in body
