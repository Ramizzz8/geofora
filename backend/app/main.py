import asyncio
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response

from app.config import Settings, get_settings
from app.countries import CountryIndex, load_countries
from app.db import connect, init_db
from app.http import get_client
from app.logs import setup_logging
from app.news.job import ingest, run_forever
from app import seo
from app.routes import router
from app.slug import slugify
from app.translate import DeepLTranslator

setup_logging()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.countries = CountryIndex(load_countries(settings.countries_path))
        # junto a countries.json: miembros de cada organización (scripts/build_organizations.py)
        app.state.organizations = json.loads(
            Path(settings.countries_path).with_name("organizations.json").read_text(encoding="utf-8"))
        app.state.db = connect(settings.db_path)
        init_db(app.state.db)
        app.state.http = get_client()
        app.state.translator = DeepLTranslator(settings.deepl_api_key, app.state.http) if settings.deepl_api_key else None
        news_task = None
        if settings.enable_scheduler:
            fips = json.loads(Path(settings.countries_path).with_name("fips.json").read_text(encoding="utf-8"))
            news_task = asyncio.create_task(run_forever(
                lambda: ingest(app.state.db, app.state.http, fips),
                settings.news_interval_min * 60,
            ))
        yield
        if news_task:
            news_task.cancel()
        await app.state.http.aclose()
        app.state.db.close()

    app = FastAPI(title="GEOFORA API", lifespan=lifespan)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.middleware("http")
    async def api_not_indexed(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["X-Robots-Tag"] = "noindex"
        return response

    @app.get("/sitemap.xml", include_in_schema=False)
    async def sitemap():
        xml = seo.sitemap_xml(settings.site_url, app.state.countries.all_sorted())
        return Response(xml, media_type="application/xml")

    @app.get("/robots.txt", include_in_schema=False)
    async def robots():
        return PlainTextResponse(seo.robots_txt(settings.site_url))

    app.include_router(router)
    if settings.static_dir:
        mount_frontend(app, Path(settings.static_dir), settings.site_url)
    return app


def _territories_on_map(root: Path) -> dict[str, str]:
    """Slug y nombre de lo que se puede pulsar en el globo, tenga ficha o no."""
    geojson = root / "data" / "countries.geojson"
    if not geojson.is_file():
        return {}
    features = json.loads(geojson.read_text(encoding="utf-8"))["features"]
    return {f["properties"]["slug"]: f["properties"]["name_es"] for f in features}


def mount_frontend(app: FastAPI, dist: Path, site_url: str) -> None:
    root = dist.resolve()
    template = (root / "index.html").read_text(encoding="utf-8")
    territories = _territories_on_map(root)

    def page(meta: seo.PageMeta, status_code: int = 200) -> HTMLResponse:
        return HTMLResponse(seo.render_page(template, meta), status_code=status_code)

    def country_page(slug: str, requested: str) -> Response:
        country = app.state.countries.by_slug(slug)
        if country is None:
            name = territories.get(slugify(slug))
            return page(seo.territory_meta(name)) if name else page(seo.not_found_meta(), 404)
        canonical = f"pais/{country.slug}"
        if requested != canonical:  # /pais/Japón, /pais/japon/
            return RedirectResponse(f"/{canonical}", status_code=301)
        return page(seo.country_meta(site_url, country))

    @app.get("/{path:path}", include_in_schema=False)
    async def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404)
        file = (root / path).resolve()
        if file.is_file() and file.is_relative_to(root) and file != root / "index.html":
            return FileResponse(file)
        if path == "":
            return page(seo.home_meta(site_url))
        if path == "legal":
            return page(seo.legal_meta(site_url))
        country = re.fullmatch(r"pais/([^/]+)/?", path)
        if country:
            return country_page(country.group(1), path)
        # cualquier otra ruta la resuelve React
        return page(seo.home_meta(site_url))
