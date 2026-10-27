import httpx
import pytest
import respx

from app.countries import Country
from app.db import connect, init_db
from app.photos import COMMONS_API, VOYAGE_URL, WIKI_URL, get_photos

MNG = Country("MNG", "MN", "mongolia", "Mongolia", "Mongolia", "Ulan Bator", [], [], None, [], None)


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "p.db"))
    init_db(c)
    return c


def media(*titles):
    return {"items": [{"type": "image", "title": t} for t in titles]}


def commons(*files):
    return {"query": {"pages": [
        {"title": f.replace("_", " "), "imageinfo": [{
            "mime": "image/jpeg",
            "thumburl": f"https://thumb/{f}",
            "descriptionurl": f"https://commons/{f}",
            "extmetadata": {
                "Artist": {"value": '<a href="//commons.wikimedia.org/wiki/User:Ana">Ana</a>'},
                "LicenseShortName": {"value": "CC BY-SA 4.0"},
            },
        }]}
        for f in files
    ]}}


@respx.mock
async def test_filters_maps_flags_and_military(conn):
    respx.get(f"{VOYAGE_URL}/Mongolia").mock(return_value=httpx.Response(200, json=media(
        "File:Mongolia_regions_map.png", "File:LocationMongolia.png", "File:USMC-100903-M-1294R-001.jpg",
        "File:Naadam_Festival.jpg", "File:Khövsgöl_Lake.JPG", "File:Visa_policy_of_Mongolia.jpg",
        "File:Gobi_dunes.jpeg", "File:Erbil_International_Airport.jpg", "File:MIAT_Boeing_737.jpg",
        "File:Iraqi_Coastal_Border_Guards.jpg", "File:AtomicEffects-p42a.jpg", "File:AeroMongoliaFokker50.jpg",
    )))
    route = respx.get(COMMONS_API).mock(return_value=httpx.Response(200, json=commons(
        "File:Naadam_Festival.jpg", "File:Khövsgöl_Lake.JPG", "File:Gobi_dunes.jpeg")))
    async with httpx.AsyncClient() as client:
        r = await get_photos(conn, client, MNG)
    asked = route.calls.last.request.url.params["titles"].split("|")
    assert asked == ["File:Naadam_Festival.jpg", "File:Khövsgöl_Lake.JPG", "File:Gobi_dunes.jpeg"]
    first = r.value["photos"][0]
    assert first == {
        "thumb": "https://thumb/File:Naadam_Festival.jpg",
        "page": "https://commons/File:Naadam_Festival.jpg",
        "author": "Ana",
        "license": "CC BY-SA 4.0",
    }
    assert len(r.value["photos"]) == 3


@respx.mock
async def test_falls_back_to_wikipedia_when_few_photos(conn):
    respx.get(f"{VOYAGE_URL}/Mongolia").mock(return_value=httpx.Response(404))
    respx.get(f"{WIKI_URL}/Mongolia").mock(return_value=httpx.Response(200, json=media(
        "Archivo:Flag_of_Mongolia.svg", "Archivo:Ulaanbaatar.jpg")))
    route = respx.get(COMMONS_API).mock(return_value=httpx.Response(200, json=commons("File:Ulaanbaatar.jpg")))
    async with httpx.AsyncClient() as client:
        r = await get_photos(conn, client, MNG)
    assert route.calls.last.request.url.params["titles"] == "File:Ulaanbaatar.jpg"
    assert [p["thumb"] for p in r.value["photos"]] == ["https://thumb/File:Ulaanbaatar.jpg"]


@respx.mock
async def test_no_photos_is_empty_list(conn):
    respx.get(f"{VOYAGE_URL}/Mongolia").mock(return_value=httpx.Response(404))
    respx.get(f"{WIKI_URL}/Mongolia").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        r = await get_photos(conn, client, MNG)
    assert r.value == {"photos": []}


@respx.mock
def test_photos_route(client):
    respx.get(url__startswith=VOYAGE_URL).mock(return_value=httpx.Response(200, json=media("File:Fuji.jpg")))
    respx.get(url__startswith=WIKI_URL).mock(return_value=httpx.Response(404))
    respx.get(COMMONS_API).mock(return_value=httpx.Response(200, json=commons("File:Fuji.jpg")))
    body = client.get("/api/country/japon/photos").json()
    assert body["photos"][0]["author"] == "Ana"
    assert body["stale"] is False
