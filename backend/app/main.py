import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.config import Settings, get_settings
from app.countries import CountryIndex, load_countries
from app.db import connect, init_db
from app.http import get_client
from app.news.job import run_forever, run_news_cycle
from app.routes import router
from app.translate import DeepLTranslator

logging.basicConfig(level=logging.INFO)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.countries = CountryIndex(load_countries(settings.countries_path))
        app.state.db = connect(settings.db_path)
        init_db(app.state.db)
        app.state.http = get_client()
        app.state.translator = DeepLTranslator(settings.deepl_api_key, app.state.http) if settings.deepl_api_key else None
        news_task = None
        if settings.enable_scheduler:
            countries = list(app.state.countries.countries.values())
            news_task = asyncio.create_task(run_forever(
                lambda: run_news_cycle(app.state.db, app.state.http, countries),
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

    app.include_router(router)
    if settings.static_dir:
        mount_frontend(app, Path(settings.static_dir))
    return app


def mount_frontend(app: FastAPI, dist: Path) -> None:
    root = dist.resolve()
    index = root / "index.html"

    @app.get("/{path:path}", include_in_schema=False)
    async def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404)
        file = (root / path).resolve()
        if file.is_file() and file.is_relative_to(root):
            return FileResponse(file)
        # rutas de la web como /pais/afganistan: las resuelve React
        return FileResponse(index)
