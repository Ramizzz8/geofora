from pathlib import Path

from app.countries import CountryIndex, load_countries

FIXTURE = Path(__file__).parent / "fixtures" / "countries.json"


def test_by_slug_normalizes_input():
    idx = CountryIndex(load_countries(FIXTURE))
    assert idx.by_slug("Afganistán").iso3 == "AFG"


def test_by_iso3():
    idx = CountryIndex(load_countries(FIXTURE))
    assert idx.by_iso3("JPN").name_es == "Japón"


def test_list_countries_sorted(client):
    r = client.get("/api/countries")
    assert r.status_code == 200
    assert [c["name_es"] for c in r.json()] == ["Afganistán", "Japón", "Tuvalu"]
    assert r.json()[0] == {"iso3": "AFG", "slug": "afganistan", "name_es": "Afganistán", "name_en": "Afghanistan"}


def test_get_country(client):
    r = client.get("/api/country/japon")
    assert r.status_code == 200
    assert r.json()["capital"] == "Tokyo"


def test_unknown_country_404(client):
    r = client.get("/api/country/narnia")
    assert r.status_code == 404
    assert r.json() == {"detail": "País no encontrado"}


def test_list_includes_english_name(client):
    assert client.get("/api/countries").json()[0]["name_en"] == "Afghanistan"
