import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def web(settings, tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html>GEOFORA", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    settings.static_dir = str(dist)
    with TestClient(create_app(settings)) as c:
        yield c


def test_serves_index(web):
    r = web.get("/")
    assert r.status_code == 200
    assert "GEOFORA" in r.text


def test_serves_assets(web):
    assert web.get("/assets/app.js").text == "console.log(1)"


def test_spa_route_falls_back_to_index(web):
    r = web.get("/pais/afganistan")
    assert r.status_code == 200
    assert "GEOFORA" in r.text


def test_api_not_shadowed(web):
    assert web.get("/api/health").json() == {"status": "ok"}
    assert web.get("/api/no-existe").status_code == 404


def test_no_path_traversal(web):
    assert "GEOFORA" in web.get("/..%2F..%2Fpyproject.toml").text
