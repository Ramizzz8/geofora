import httpx
import respx

from app.music import DEEZER_TRACK_URL, DEEZER_URL, LASTFM_URL, MB_URL


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


@respx.mock
def test_music_route_points_preview_to_our_server(client):
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json={"artists": [{"id": "mb1", "name": "Hikaru Utada"}]}))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": [
        {"id": 3135556, "preview": "https://cdnt-preview.dzcdn.net/a.mp3?hdnea=exp=1", "link": "https://deezer.com/track/3135556",
         "artist": {"name": "Hikaru Utada"}}]}))
    item = client.get("/api/country/japon/music").json()["items"][0]
    assert item["preview_url"] == "/api/music/preview/3135556"


@respx.mock
def test_preview_redirects_to_fresh_deezer_url(client):
    fresh = "https://cdnt-preview.dzcdn.net/a.mp3?hdnea=exp=9999999999"
    respx.get(f"{DEEZER_TRACK_URL}/3135556").mock(return_value=httpx.Response(200, json={"id": 3135556, "preview": fresh}))
    r = client.get("/api/music/preview/3135556", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == fresh
    assert r.headers["cache-control"] == "no-store"


@respx.mock
def test_preview_without_audio_is_404(client):
    respx.get(f"{DEEZER_TRACK_URL}/42").mock(return_value=httpx.Response(200, json={"id": 42, "preview": ""}))
    assert client.get("/api/music/preview/42", follow_redirects=False).status_code == 404


@respx.mock
def test_preview_deezer_down_is_503(client):
    respx.get(f"{DEEZER_TRACK_URL}/42").mock(side_effect=httpx.ConnectError("down"))
    assert client.get("/api/music/preview/42", follow_redirects=False).status_code == 503
