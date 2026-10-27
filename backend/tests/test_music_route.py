import httpx
import respx

from app.music import LASTFM_URL, MB_URL


@respx.mock
def test_music_route_returns_503_when_unavailable(client):
    respx.get(LASTFM_URL).mock(side_effect=httpx.ConnectError("down"))
    respx.get(MB_URL).mock(side_effect=httpx.ConnectError("down"))
    r = client.get("/api/country/japon/music")
    assert r.status_code == 503


@respx.mock
def test_music_route_shape(client):
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json={"artists": []}))
    body = client.get("/api/country/japon/music").json()
    assert body["source"] == "none"
    assert body["stale"] is False
    assert "fetched_at" in body
