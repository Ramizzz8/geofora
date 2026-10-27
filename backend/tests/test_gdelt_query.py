import httpx
import respx

from app.countries import Country
from app.news.gdelt import GDELT_URL, fetch_country_news

AFG = Country("AFG", "AF", "afganistan", "Afganistán", "Afghanistan", "Kabul", [], [], None, [], None)
USA = Country("USA", "US", "estados-unidos", "Estados Unidos", "United States", None, [], [], None, [], None)


def articles(prefix, n):
    return {"articles": [
        {"url": f"https://{prefix}/{i}", "title": f"{prefix} {i}", "seendate": "20261027T081500Z",
         "domain": prefix, "language": "English", "sourcecountry": "X"}
        for i in range(n)
    ]}


async def no_sleep(_):
    pass


def queries(route):
    return [c.request.url.params["query"] for c in route.calls]


@respx.mock
async def test_local_media_query_first():
    route = respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json=articles("local", 6)))
    async with httpx.AsyncClient() as client:
        arts = await fetch_country_news(client, USA, sleep=no_sleep)
    # con suficientes noticias de medios del país no hace falta la búsqueda general
    assert queries(route) == ['"United States" sourcecountry:unitedstates']
    assert len(arts) == 6


@respx.mock
async def test_falls_back_to_mentions_when_few_local():
    route = respx.get(GDELT_URL).mock(side_effect=[
        httpx.Response(200, json=articles("local", 2)),
        httpx.Response(200, json=articles("world", 4)),
    ])
    slept = []

    async def sleep(s):
        slept.append(s)

    async with httpx.AsyncClient() as client:
        arts = await fetch_country_news(client, AFG, sleep=sleep)
    assert queries(route) == ['"Afghanistan" sourcecountry:afghanistan', '"Afghanistan"']
    assert slept == [5]
    assert [a.domain for a in arts] == ["local"] * 2 + ["world"] * 4
