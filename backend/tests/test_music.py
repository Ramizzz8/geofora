import httpx
import pytest
import respx

from app.countries import Country
from app.db import connect, init_db
from app.music import APPLE_URL, DEEZER_URL, MB_URL, TTL_S, get_music

COL = Country("COL", "CO", "colombia", "Colombia", "Colombia", "Bogotá", [], [], None, [], None)
FEED_URL = f"{APPLE_URL}/co/music/most-played/10/songs.json"

APPLE = {"feed": {"results": [
    {"name": "PARADIXE", "artistName": "Feid, El America",
     "artworkUrl100": "https://img.apple/art/100x100bb.jpg", "url": "https://music.apple.com/co/song/1"},
    {"name": "BbY WOW", "artistName": "KAROL G",
     "artworkUrl100": "https://img.apple/art2/100x100bb.jpg", "url": "https://music.apple.com/co/song/2"},
]}}
MB_ARTISTS = {"artists": [{"id": "mb1", "name": "Shakira"}, {"id": "mb2", "name": "Nadie"}]}


def deezer_hit(name, id_=7):
    return {"data": [{"id": id_, "preview": "https://cdn.deezer/p.mp3?hdnea=exp=1", "link": f"https://deezer.com/track/{id_}",
                      "artist": {"name": name, "picture_medium": "https://img/artist.jpg"},
                      "album": {"cover_medium": "https://img/cover.jpg"}}]}


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "m.db"))
    init_db(c)
    return c


async def no_sleep(_):
    pass


async def music(conn, **kwargs):
    async with httpx.AsyncClient() as client:
        return await get_music(conn, client, COL, sleep=no_sleep, **kwargs)


@respx.mock
async def test_chart_comes_from_apple_with_its_artwork_and_link(conn):
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, json=APPLE))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json=deezer_hit("Feid")))
    r = await music(conn)
    assert r.value["source"] == "chart"
    assert r.value["items"][0] == {
        "title": "PARADIXE", "artist": "Feid, El America", "deezer_id": 7,
        "link": "https://music.apple.com/co/song/1", "image": "https://img.apple/art/200x200bb.jpg",
    }


@respx.mock
async def test_song_from_another_artist_on_deezer_has_no_preview(conn):
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, json=APPLE))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json=deezer_hit("Alguien Distinto")))
    r = await music(conn)
    assert [i["deezer_id"] for i in r.value["items"]] == [None, None]
    assert r.value["items"][0]["image"] == "https://img.apple/art/200x200bb.jpg"


@respx.mock
async def test_deezer_error_keeps_song_without_preview(conn):
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, json=APPLE))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(500))
    r = await music(conn)
    assert r.value["items"][0]["deezer_id"] is None
    assert r.value["items"][0]["link"] == "https://music.apple.com/co/song/1"


@respx.mock
async def test_retries_when_apple_fails_at_random(conn):
    route = respx.get(FEED_URL).mock(side_effect=[
        httpx.ReadTimeout("lento"), httpx.Response(502, text="<html>"), httpx.Response(200, json=APPLE)])
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    r = await music(conn)
    assert route.call_count == 3
    assert r.value["source"] == "chart"


@respx.mock
async def test_non_json_answer_counts_as_failure(conn):
    respx.get(FEED_URL).mock(side_effect=[httpx.Response(200, text="<html>"), httpx.Response(200, json=APPLE)])
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    assert (await music(conn)).value["source"] == "chart"


@respx.mock
async def test_country_without_chart_falls_back_to_local_artists(conn):
    route = respx.get(FEED_URL).mock(return_value=httpx.Response(500, text="<html>"))
    mb = respx.get(MB_URL).mock(return_value=httpx.Response(200, json=MB_ARTISTS))
    respx.get(DEEZER_URL).mock(side_effect=lambda req: httpx.Response(
        200, json=deezer_hit("Shakira") if req.url.params["q"] == "Shakira" else {"data": []}))
    r = await music(conn)
    assert route.call_count == 3
    assert mb.calls.last.request.url.params["query"] == 'area:"Colombia"'
    assert r.value["source"] == "artists"
    assert r.value["items"][0] == {"title": None, "artist": "Shakira", "deezer_id": 7,
                                   "image": "https://img/artist.jpg", "link": "https://deezer.com/track/7"}
    assert r.value["items"][1]["deezer_id"] is None


@respx.mock
async def test_nothing_found_is_none(conn):
    respx.get(FEED_URL).mock(return_value=httpx.Response(500))
    respx.get(MB_URL).mock(return_value=httpx.Response(200, json={"artists": []}))
    assert (await music(conn)).value == {"source": "none", "items": []}


@respx.mock
async def test_refreshes_after_a_day_and_serves_stale_if_all_is_down(conn):
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, json=APPLE))
    respx.get(DEEZER_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    await music(conn, now=lambda: 1000.0)
    assert TTL_S == 86400
    respx.get(FEED_URL).mock(side_effect=httpx.ConnectError("caído"))
    respx.get(MB_URL).mock(side_effect=httpx.ConnectError("caído"))
    r = await music(conn, now=lambda: 1000.0 + TTL_S + 1)
    assert r.stale is True
    assert r.value["source"] == "chart"
