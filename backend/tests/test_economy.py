import httpx
import pytest
import respx

from app.countries import Country
from app.db import connect, init_db
from app.economy import IMF_DEBT_URL, WB_URL, get_economy

JPN = Country("JPN", "JP", "japon", "Japón", "Japan", "Tokyo", [], [], None, [], None)
UNK = Country("UNK", "XK", "kosovo", "Kosovo", "Kosovo", "Pristina", [], [], None, [], None)
NOW = 1_793_000_000.0  # octubre de 2026


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "e.db"))
    init_db(c)
    return c


def wb(rows):
    return [{"page": 1}, [{"date": str(y), "value": v, "countryiso3code": "JPN"} for y, v in rows]]


IMF = {"values": {"GGXWDG_NGDP": {
    # 2026 es el año en curso (estimación) y 2027 una proyección: no son datos cerrados
    "JPN": {"2010": 205.9, "2024": 236.7, "2025": 234.9, "2026": 233.0, "2027": 230.0},
    "AFG": {"2024": 7.0},
}}}


def mock_world_bank(gdp=None, fail=()):
    def handler(request):
        indicator = request.url.path.rsplit("/", 1)[1]
        if indicator in fail:
            return httpx.Response(500)
        if indicator == "NY.GDP.MKTP.CD":
            return httpx.Response(200, json=wb(gdp or [(2025, 4.43e12), (2024, None), (2023, 4.2e12), (2010, 5.7e12)]))
        return httpx.Response(200, json=wb([(2025, 3.2)]))
    return respx.get(url__startswith=WB_URL).mock(side_effect=handler)


@respx.mock
async def test_latest_value_and_series_from_2010(conn):
    mock_world_bank()
    respx.get(IMF_DEBT_URL).mock(return_value=httpx.Response(200, json=IMF))
    async with httpx.AsyncClient() as client:
        r = await get_economy(conn, client, JPN, now=lambda: NOW)
    gdp = next(i for i in r.value["indicators"] if i["id"] == "gdp")
    assert gdp["year"] == 2025 and gdp["value"] == 4.43e12
    assert gdp["unit"] == "usd"
    # los años sin dato se omiten y la serie va de más antiguo a más reciente
    assert gdp["series"] == [[2010, 5.7e12], [2023, 4.2e12], [2025, 4.43e12]]
    assert [i["id"] for i in r.value["indicators"]] == ["gdp", "gdp_pc", "inflation", "unemployment", "debt"]


@respx.mock
async def test_debt_ignores_imf_projections(conn):
    mock_world_bank()
    respx.get(IMF_DEBT_URL).mock(return_value=httpx.Response(200, json=IMF))
    async with httpx.AsyncClient() as client:
        r = await get_economy(conn, client, JPN, now=lambda: NOW)
    debt = next(i for i in r.value["indicators"] if i["id"] == "debt")
    assert debt["year"] == 2025 and debt["value"] == 234.9
    assert debt["series"][-1] == [2025, 234.9]


@respx.mock
async def test_imf_dataset_downloaded_once_for_all_countries(conn):
    mock_world_bank()
    imf = respx.get(IMF_DEBT_URL).mock(return_value=httpx.Response(200, json=IMF))
    afg = Country("AFG", "AF", "afganistan", "Afganistán", "Afghanistan", "Kabul", [], [], None, [], None)
    async with httpx.AsyncClient() as client:
        await get_economy(conn, client, JPN, now=lambda: NOW)
        await get_economy(conn, client, afg, now=lambda: NOW)
    assert imf.call_count == 1


@respx.mock
async def test_failed_indicator_is_omitted(conn):
    mock_world_bank(fail={"SL.UEM.TOTL.ZS"})
    respx.get(IMF_DEBT_URL).mock(return_value=httpx.Response(500))
    async with httpx.AsyncClient() as client:
        r = await get_economy(conn, client, JPN, now=lambda: NOW)
    assert [i["id"] for i in r.value["indicators"]] == ["gdp", "gdp_pc", "inflation"]


@respx.mock
async def test_all_sources_down_raises(conn):
    respx.get(url__startswith=WB_URL).mock(side_effect=httpx.ConnectError("down"))
    respx.get(IMF_DEBT_URL).mock(side_effect=httpx.ConnectError("down"))
    async with httpx.AsyncClient() as client:
        with pytest.raises(Exception):
            await get_economy(conn, client, JPN, now=lambda: NOW)


@respx.mock
async def test_kosovo_uses_world_bank_code(conn):
    route = mock_world_bank()
    respx.get(IMF_DEBT_URL).mock(return_value=httpx.Response(200, json=IMF))
    async with httpx.AsyncClient() as client:
        await get_economy(conn, client, UNK, now=lambda: NOW)
    assert all("/country/XKX/" in str(c.request.url) for c in route.calls)


@respx.mock
def test_economy_route(client):
    mock_world_bank()
    respx.get(IMF_DEBT_URL).mock(return_value=httpx.Response(200, json=IMF))
    body = client.get("/api/country/japon/economy").json()
    assert body["indicators"][0]["label"] == "PIB"
    assert body["stale"] is False
