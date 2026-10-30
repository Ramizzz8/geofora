import httpx
import pytest
import respx

from app.countries import Country
from app.culture import SUMMARY_URL, get_culture
from app.db import connect, init_db

JPN = Country("JPN", "JP", "japon", "Japón", "Japan", "Tokyo", [], [], None, [], None)
GEO = Country("GEO", "GE", "georgia", "Georgia", "Georgia", "Tbilisi", [], [], None, [], None)


def summary(title, extract="Texto", kind="standard"):
    return {
        "type": kind, "title": title, "extract": extract,
        "thumbnail": {"source": f"https://img/{title}.png"},
        "content_urls": {"desktop": {"page": f"https://es.wikipedia.org/wiki/{title}"}},
    }


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "w.db"))
    init_db(c)
    return c


@respx.mock
async def test_summary_and_culture_link(conn):
    respx.get(f"{SUMMARY_URL}/Japón").mock(return_value=httpx.Response(200, json=summary("Japón", "Japón es un país insular")))
    respx.get(f"{SUMMARY_URL}/Cultura_de_Japón").mock(return_value=httpx.Response(200, json=summary("Cultura_de_Japón")))
    async with httpx.AsyncClient() as client:
        r = await get_culture(conn, client, JPN)
    assert r.value == {
        "extract": "Japón es un país insular",
        "thumbnail": "https://img/Japón.png",
        "page_url": "https://es.wikipedia.org/wiki/Japón",
        "culture_url": "https://es.wikipedia.org/wiki/Cultura_de_Japón",
    }


@respx.mock
async def test_culture_url_none_when_missing(conn):
    respx.get(f"{SUMMARY_URL}/Japón").mock(return_value=httpx.Response(200, json=summary("Japón")))
    respx.get(f"{SUMMARY_URL}/Cultura_de_Japón").mock(return_value=httpx.Response(404, json={}))
    async with httpx.AsyncClient() as client:
        r = await get_culture(conn, client, JPN)
    assert r.value["culture_url"] is None


@respx.mock
async def test_disambiguation_retries_with_pais(conn):
    respx.get(f"{SUMMARY_URL}/Georgia").mock(return_value=httpx.Response(200, json=summary("Georgia", kind="disambiguation")))
    respx.get(f"{SUMMARY_URL}/Georgia_(país)").mock(return_value=httpx.Response(200, json=summary("Georgia_(país)", "País del Cáucaso")))
    respx.get(f"{SUMMARY_URL}/Cultura_de_Georgia").mock(return_value=httpx.Response(404, json={}))
    async with httpx.AsyncClient() as client:
        r = await get_culture(conn, client, GEO)
    assert r.value["extract"] == "País del Cáucaso"


@respx.mock
async def test_english_uses_english_wikipedia_and_separate_cache(conn):
    en = "https://en.wikipedia.org/api/rest_v1/page/summary"
    page = respx.get(f"{en}/Japan").mock(return_value=httpx.Response(200, json=summary("Japan", "Japan is an island country")))
    respx.get(f"{en}/Culture_of_Japan").mock(return_value=httpx.Response(200, json=summary("Culture_of_Japan")))
    respx.get(f"{SUMMARY_URL}/Japón").mock(return_value=httpx.Response(200, json=summary("Japón", "Japón es un país insular")))
    respx.get(f"{SUMMARY_URL}/Cultura_de_Japón").mock(return_value=httpx.Response(404, json={}))
    async with httpx.AsyncClient() as client:
        r_en = await get_culture(conn, client, JPN, lang="en")
        r_es = await get_culture(conn, client, JPN)
        await get_culture(conn, client, JPN, lang="en")
    assert r_en.value["extract"] == "Japan is an island country"
    assert r_en.value["culture_url"].endswith("Culture_of_Japan")
    assert r_es.value["extract"] == "Japón es un país insular"
    assert page.call_count == 1


@respx.mock
async def test_english_disambiguation_retries_with_country(conn):
    en = "https://en.wikipedia.org/api/rest_v1/page/summary"
    respx.get(f"{en}/Georgia").mock(return_value=httpx.Response(200, json=summary("Georgia", kind="disambiguation")))
    respx.get(f"{en}/Georgia_(country)").mock(return_value=httpx.Response(200, json=summary("Georgia_(country)", "Country in the Caucasus")))
    respx.get(f"{en}/Culture_of_Georgia").mock(return_value=httpx.Response(404, json={}))
    async with httpx.AsyncClient() as client:
        r = await get_culture(conn, client, GEO, lang="en")
    assert r.value["extract"] == "Country in the Caucasus"
