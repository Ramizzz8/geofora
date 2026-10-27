import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.config import Settings, get_settings
from app.countries import CountryIndex, load_countries
from app.db import connect, init_db
from app.http import get_client
from app.news.job import run_news_cycle
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
        scheduler = None
        if settings.enable_scheduler:
            scheduler = AsyncIOScheduler()
            scheduler.add_job(
                run_news_cycle,
                "interval",
                minutes=settings.news_interval_min,
                args=[app.state.db, app.state.http, list(app.state.countries.countries.values())],
                next_run_time=datetime.now(),
                max_instances=1,
                coalesce=True,
            )
            scheduler.start()
        yield
        if scheduler:
            scheduler.shutdown(wait=False)
        await app.state.http.aclose()
        app.state.db.close()

    app = FastAPI(title="GEOFORA API", lifespan=lifespan)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    app.include_router(router)
    return app
