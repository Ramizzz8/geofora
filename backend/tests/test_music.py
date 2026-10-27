import httpx
import pytest
import respx

from app.countries import Country
from app.db import connect, init_db
from app.music import DEEZER_URL, LASTFM_URL, MB_URL, get_music

AFG = Country("AFG", "AF", "afganistan", "Afganistán", "Afghanistan", "Kabul", [], [], None, [], None)

LASTFM_CHART = {"tracks": {"track": [
    {"name": "Song A", "artist": {"name": "Artist A"}, "url": "https://last.fm/a"},
    {"name": "Song B", "artist": {"name": "Artist B"}, "url": "https://last.fm/b"},
]}}
LASTFM_EMPTY = {"tracks": {"track": []}}
MB_ARTISTS = {"artists": [{"id": "mb1", "name": "Ahmad Zahir"}]}
DEEZER_HIT = {"data": [{"preview": "https://cdn.deezer/p.mp3", "link": "https://deezer.com/track/1"}]}


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "m.db"))
    init_db(c)
    return c


@respx.mock
async def test_chart_with_previews(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_CHART))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json=DEEZER_HIT))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert r.value["source"] == "chart"
    first = r.value["items"][0]
    assert first == {"title": "Song A", "artist": "Artist A", "preview_url": "https://cdn.deezer/p.mp3",
                     "link": "https://deezer.com/track/1"}


@respx.mock
async def test_falls_back_to_artists(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_EMPTY))
    mb = respx.get(MB_URL).mock(return_value=httpx.Response(200, json=MB_ARTISTS))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert mb.calls.last.request.url.params["query"] == 'area:"Afghanistan"'
    assert r.value["source"] == "artists"
    assert r.value["items"] == [{"title": None, "artist": "Ahmad Zahir", "preview_url": None,
                                 "link": "https://musicbrainz.org/artist/mb1"}]


@respx.mock
async def test_none_when_nothing_found(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_EMPTY))
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json={"artists": []}))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert r.value == {"source": "none", "items": []}


@respx.mock
async def test_without_lastfm_key_skips_chart(conn):
    lastfm = respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_CHART))
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json=MB_ARTISTS))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "")
    assert not lastfm.called
    assert r.value["source"] == "artists"


@respx.mock
async def test_deezer_error_keeps_item_without_preview(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_CHART))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(500))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert r.value["items"][0]["preview_url"] is None
    assert r.value["items"][0]["link"] == "https://last.fm/a"


@respx.mock
async def test_timeout_serves_stale(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_CHART))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json=DEEZER_HIT))
    async with httpx.AsyncClient() as client:
        await get_music(conn, client, AFG, "key", now=lambda: 1000.0)
    respx.get(LASTFM_URL).mock(side_effect=httpx.ReadTimeout("timeout"))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key", now=lambda: 1000.0 + 6 * 86400)
    assert r.stale is True
    assert r.value["source"] == "chart"
