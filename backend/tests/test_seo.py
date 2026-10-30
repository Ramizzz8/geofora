import json
import re
import xml.etree.ElementTree as ET

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

SITE = "https://geofora.andresrami.com"
INDEX = """<!doctype html>
<html lang="es">
  <head>
    <meta name="description" content="Descripcion original" />
    <title>GEOFORA</title>
    <script data-goatcounter="https://stats" async src="https://stats/count.js"></script>
  </head>
  <body><div id="root"></div></body>
</html>"""
GEOJSON = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": None,
     "properties": {"iso3": "JPN", "name_es": "Japón", "name_en": "Japan", "slug": "japon"}},
    {"type": "Feature", "geometry": None,
     "properties": {"iso3": "SOL", "name_es": "Somaliland", "name_en": "Somaliland", "slug": "somaliland"}},
]}


@pytest.fixture
def web(settings, tmp_path):
    dist = tmp_path / "dist"
    (dist / "data").mkdir(parents=True)
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    (dist / "data" / "countries.geojson").write_text(json.dumps(GEOJSON), encoding="utf-8")
    settings.static_dir = str(dist)
    with TestClient(create_app(settings)) as c:
        yield c


def test_sitemap_is_xml_with_home_legal_and_every_country(web):
    r = web.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text for e in ET.fromstring(r.text).findall("s:url/s:loc", ns)]
    assert locs == [f"{SITE}/", f"{SITE}/legal", f"{SITE}/pais/afganistan", f"{SITE}/pais/japon", f"{SITE}/pais/tuvalu"]


def test_sitemap_leaves_out_territories_without_data(web):
    assert "somaliland" not in web.get("/sitemap.xml").text


def test_robots_allows_crawling_and_points_to_sitemap(web):
    r = web.get("/robots.txt")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert "User-agent: *" in r.text
    assert f"Sitemap: {SITE}/sitemap.xml" in r.text
    # la web necesita /api para pintarse: bloquearlo impediría a Google ver el contenido
    assert "Disallow: /api" not in r.text


def test_api_can_be_crawled_but_not_indexed(web):
    assert web.get("/api/countries").headers["x-robots-tag"] == "noindex"
    assert "x-robots-tag" not in web.get("/pais/japon").headers


def test_country_page_has_its_metadata_in_the_initial_html(web):
    r = web.get("/pais/japon")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    html = r.text
    assert "<title>Japón: noticias, música y economía · GEOFORA</title>" in html
    assert "Descripcion original" not in html
    assert re.search(r'<meta name="description" content="[^"]*Japón[^"]*"', html)
    assert f'<link rel="canonical" href="{SITE}/pais/japon"' in html
    assert '<meta property="og:title" content="Japón: noticias, música y economía · GEOFORA"' in html
    assert f'<meta property="og:url" content="{SITE}/pais/japon"' in html
    assert '<meta property="og:image" content="https://flagcdn.com/w640/jp.png"' in html
    assert '<meta property="og:type" content="website"' in html
    assert 'name="robots"' not in html
    # lo demás del documento sigue intacto
    assert 'data-goatcounter="https://stats"' in html and '<div id="root"></div>' in html


def test_values_are_escaped(web):
    name = 'A&B "<script>alert(1)</script>'
    web.app.state.countries.by_slug("japon").name_es = name
    html = web.get("/pais/japon").text
    assert "<script>alert(1)" not in html
    assert "A&amp;B &quot;&lt;script&gt;" in html


def test_home_and_legal_have_their_own_metadata(web):
    home = web.get("/").text
    assert "<title>GEOFORA: el mundo, país a país</title>" in home
    assert f'<link rel="canonical" href="{SITE}/"' in home
    legal = web.get("/legal").text
    assert "<title>Aviso legal y privacidad · GEOFORA</title>" in legal
    assert f'<link rel="canonical" href="{SITE}/legal"' in legal


def test_unknown_country_is_404_without_inventing_a_country(web):
    r = web.get("/pais/narnia")
    assert r.status_code == 404
    assert '<div id="root"></div>' in r.text  # React sigue mostrando «País no encontrado»
    assert "<title>País no encontrado · GEOFORA</title>" in r.text
    assert '<meta name="robots" content="noindex"' in r.text
    assert "canonical" not in r.text and "og:title" not in r.text
    assert "narnia" not in r.text


def test_accented_or_uppercase_url_redirects_to_canonical(web):
    r = web.get("/pais/Jap%C3%B3n", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/pais/japon"


def test_territory_on_the_map_without_data_is_not_indexed(web):
    r = web.get("/pais/somaliland")
    assert r.status_code == 200
    assert "<title>Somaliland · GEOFORA</title>" in r.text
    assert '<meta name="robots" content="noindex"' in r.text


def test_static_files_still_served(web):
    r = web.get("/data/countries.geojson")
    assert r.status_code == 200 and json.loads(r.text)["type"] == "FeatureCollection"
