import httpx
import respx

from app.culture import SUMMARY_URL


@respx.mock
def test_culture_route(client):
    respx.get(url__startswith=f"{SUMMARY_URL}/Cultura").mock(return_value=httpx.Response(404, json={}))
    respx.get(url__startswith=SUMMARY_URL).mock(return_value=httpx.Response(200, json={
        "type": "standard", "extract": "Texto",
        "content_urls": {"desktop": {"page": "https://es.wikipedia.org/wiki/Jap%C3%B3n"}},
    }))
    body = client.get("/api/country/japon/culture").json()
    assert body["extract"] == "Texto"
    assert body["culture_url"] is None
    assert body["stale"] is False


@respx.mock
def test_culture_route_503(client):
    respx.get(url__startswith=SUMMARY_URL).mock(side_effect=httpx.ConnectError("down"))
    assert client.get("/api/country/japon/culture").status_code == 503
