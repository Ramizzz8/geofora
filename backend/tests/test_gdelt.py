import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
import respx

from app.countries import Country
from app.news.gdelt import GDELT_URL, fetch_country_news

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "gdelt_afg.json").read_text(encoding="utf-8"))


async def no_sleep(_):
    pass


AFG = Country("AFG", "AF", "afganistan", "Afganistán", "Afghanistan", "Kabul", [], [], None, [], None)


@respx.mock
async def test_parses_articles_and_dedupes():
    route = respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json=FIXTURE))
    async with httpx.AsyncClient() as client:
        articles = await fetch_country_news(client, AFG, sleep=no_sleep)
    assert route.calls[0].request.url.params["query"] == '"Afghanistan" sourcecountry:afghanistan'
    # duplicado por URL y duplicado por título normalizado eliminados
    assert [a.url for a in articles] == ["https://tolonews.com/a1", "https://aljazeera.net/a2", "https://elpais.com/a3"]
    first = articles[0]
    assert first.seen_at == datetime(2026, 10, 27, 8, 15, tzinfo=timezone.utc).timestamp()
    assert first.source_country == "Afghanistan"


@respx.mock
async def test_maps_language_to_iso():
    respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json=FIXTURE))
    async with httpx.AsyncClient() as client:
        articles = await fetch_country_news(client, AFG, sleep=no_sleep)
    assert [a.language for a in articles] == ["en", "ar", "es"]


@respx.mock
async def test_empty_response_returns_empty_list():
    respx.get(GDELT_URL).mock(return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        assert await fetch_country_news(client, AFG, sleep=no_sleep) == []


@respx.mock
async def test_rate_limit_text_raises():
    # GDELT responde 200 con texto plano cuando se le pide demasiado rápido
    respx.get(GDELT_URL).mock(return_value=httpx.Response(200, text="Please limit requests to one every 5 seconds"))
    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await fetch_country_news(client, AFG, sleep=no_sleep)
