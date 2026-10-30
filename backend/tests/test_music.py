import httpx
import pytest
import respx

from app.countries import Country
from app.db import connect, init_db
from app.music import DEEZER_URL, LASTFM_URL, MB_URL, get_music

AFG = Country("AFG", "AF", "afganistan", "Afganistán", "Afghanistan", "Kabul", [], [], None, [], None)

LASTFM_CHART = {"tracks": {"track": [
    {"name": "Song A", "artist": {"name": "Artist A"}, "url": "https://last.fm/a", "listeners": "58213"},
    {"name": "Song B", "artist": {"name": "Artist B"}, "url": "https://last.fm/b"},
]}}
LASTFM_EMPTY = {"tracks": {"track": []}}
MB_ARTISTS = {"artists": [{"id": "mb1", "name": "Ahmad Zahir"}]}
DEEZER_HIT = {"data": [{"id": 3135556, "preview": "https://cdn.deezer/p.mp3?hdnea=exp=1", "link": "https://deezer.com/track/1",
                         "artist": {"name": "Artist A", "picture_medium": "https://img/artist.jpg"},
                         "album": {"cover_medium": "https://img/cover.jpg"}}]}


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
    # se guarda el id de Deezer, no el enlace del fragmento, que caduca en ~1 h
    assert first == {"title": "Song A", "artist": "Artist A", "deezer_id": 3135556,
                     "link": "https://deezer.com/track/1", "listeners": 58213, "image": "https://img/cover.jpg"}


@respx.mock
async def test_falls_back_to_artists(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_EMPTY))
    mb = respx.get(MB_URL).mock(return_value=httpx.Response(200, json=MB_ARTISTS))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert mb.calls.last.request.url.params["query"] == 'area:"Afghanistan"'
    assert r.value["source"] == "artists"
    assert r.value["items"] == [{"title": None, "artist": "Ahmad Zahir", "deezer_id": None, "listeners": None, "image": None,
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
    assert r.value["items"][0]["deezer_id"] is None
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


@respx.mock
async def test_lastfm_error_does_not_expose_key(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(500, json={}))
    async with httpx.AsyncClient() as client:
        with pytest.raises(Exception) as exc:
            await get_music(conn, client, AFG, "SECRETKEY123")
    assert "SECRETKEY123" not in str(exc.value)
    assert "SECRETKEY123" not in repr(exc.value)
    # la excepción original (con la URL completa) no se encadena en el traceback
    assert exc.value.__cause__ is None and exc.value.__suppress_context__


@respx.mock
async def test_track_search_uses_plain_query_and_checks_artist(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json={"tracks": {"track": [
        {"name": "Housewife", "artist": {"name": "Tate McRae"}, "url": "https://last.fm/h"},
        {"name": "Otra", "artist": {"name": "Nadie Conocido"}, "url": "https://last.fm/o"},
    ]}}))

    def deezer(request):
        q = request.url.params["q"]
        if q == "Tate McRae Housewife":
            return httpx.Response(200, json={"data": [{"id": 7, "preview": "https://p/7.mp3", "link": "https://deezer.com/track/7",
                                                       "artist": {"name": "Tate McRae"}}]})
        # para la otra canción Deezer devuelve una de otro artista: no se debe aceptar
        return httpx.Response(200, json={"data": [{"id": 9, "preview": "https://p/9.mp3", "link": "https://deezer.com/track/9",
                                                   "artist": {"name": "Alguien Distinto"}}]})

    route = respx.get(DEEZER_URL).mock(side_effect=deezer)
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert "Tate McRae Housewife" in [c.request.url.params["q"] for c in route.calls]
    assert [i["deezer_id"] for i in r.value["items"]] == [7, None]


@respx.mock
async def test_artist_mode_uses_artist_picture(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_EMPTY))
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json=MB_ARTISTS))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": [{
        "id": 5, "preview": "https://p/5.mp3", "link": "https://deezer.com/track/5",
        "artist": {"name": "Ahmad Zahir", "picture_medium": "https://img/zahir.jpg"},
        "album": {"cover_medium": "https://img/album.jpg"}}]}))
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "key")
    assert r.value["items"][0]["image"] == "https://img/zahir.jpg"


@respx.mock
async def test_artist_mode_uses_plain_query_and_checks_artist(conn):
    respx.get(LASTFM_URL).mock(return_value=httpx.Response(200, json=LASTFM_EMPTY))
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json={"artists": [
        {"id": "a", "name": "Vicente Fernández"}, {"id": "b", "name": "Nadie"}]}))

    def deezer(request):
        q = request.url.params["q"]
        name = "Vicente Fernández" if q == "Vicente Fernández" else "Otro Artista"
        return httpx.Response(200, json={"data": [{"id": 1 if name.startswith("V") else 2, "preview": "https://p.mp3",
                                                   "link": "https://d", "artist": {"name": name, "picture_medium": "https://img"}}]})

    route = respx.get(DEEZER_URL).mock(side_effect=deezer)
    async with httpx.AsyncClient() as client:
        r = await get_music(conn, client, AFG, "")
    assert "Vicente Fernández" in [c.request.url.params["q"] for c in route.calls]
    assert [i["deezer_id"] for i in r.value["items"]] == [1, None]
