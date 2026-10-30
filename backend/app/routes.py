import logging
import time
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.countries import Country
from app.culture import get_culture
from app.economy import get_economy
from app.music import fresh_preview, get_music
from app.photos import get_photos
from app.news.store import heatmap, last_seen, recent_articles
from app.translate import translate_titles

log = logging.getLogger(__name__)

# todos los endpoints son async: la conexión SQLite se usa solo desde el event loop
router = APIRouter(prefix="/api")


def get_country_or_404(request: Request, slug: str) -> Country:
    country = request.app.state.countries.by_slug(slug)
    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return country


@router.get("/countries")
async def list_countries(request: Request):
    return [
        {"iso3": c.iso3, "slug": c.slug, "name_es": c.name_es}
        for c in request.app.state.countries.all_sorted()
    ]


@router.get("/country/{slug}")
async def get_country(request: Request, slug: str):
    return get_country_or_404(request, slug).to_dict()


@router.get("/heatmap")
async def get_heatmap(request: Request):
    db = request.app.state.db
    return {"counts": heatmap(db, time.time()), "updated_at": last_seen(db)}


@router.get("/country/{slug}/news")
async def get_news(request: Request, slug: str):
    country = get_country_or_404(request, slug)
    db = request.app.state.db
    articles, rng = recent_articles(db, country.iso3, time.time())
    out = await translate_titles(db, request.app.state.translator, articles)
    return {"range": rng, "articles": [asdict(a) for a in out], "updated_at": last_seen(db)}


def unavailable(section: str) -> HTTPException:
    return HTTPException(status_code=503, detail=f"{section} no disponible ahora mismo")


@router.get("/country/{slug}/music")
async def get_country_music(request: Request, slug: str):
    country = get_country_or_404(request, slug)
    state = request.app.state
    try:
        result = await get_music(state.db, state.http, country, state.settings.lastfm_api_key)
    except Exception:
        log.warning("music unavailable for %s", country.iso3, exc_info=True)
        raise unavailable("Música")
    body = result.to_response()
    body["items"] = [
        {**item, "preview_url": f"/api/music/preview/{item['deezer_id']}" if item.get("deezer_id") else None}
        for item in body["items"]
    ]
    return body


@router.get("/music/preview/{deezer_id}")
async def music_preview(request: Request, deezer_id: int):
    try:
        url = await fresh_preview(request.app.state.http, deezer_id)
    except Exception:
        log.warning("deezer preview unavailable for %s", deezer_id, exc_info=True)
        raise unavailable("Música")
    if not url:
        raise HTTPException(status_code=404, detail="Esta canción no tiene fragmento")
    # sin caché: el enlace de Deezer caduca y siempre hay que pedir uno nuevo
    return RedirectResponse(url, status_code=302, headers={"Cache-Control": "no-store"})


@router.get("/country/{slug}/culture")
async def get_country_culture(request: Request, slug: str):
    country = get_country_or_404(request, slug)
    state = request.app.state
    try:
        result = await get_culture(state.db, state.http, country)
    except Exception:
        log.warning("culture unavailable for %s", country.iso3, exc_info=True)
        raise unavailable("Cultura")
    return result.to_response()


@router.get("/country/{slug}/photos")
async def get_country_photos(request: Request, slug: str):
    country = get_country_or_404(request, slug)
    state = request.app.state
    try:
        result = await get_photos(state.db, state.http, country)
    except Exception:
        log.warning("photos unavailable for %s", country.iso3, exc_info=True)
        raise unavailable("Fotos")
    return result.to_response()


@router.get("/country/{slug}/economy")
async def get_country_economy(request: Request, slug: str):
    country = get_country_or_404(request, slug)
    state = request.app.state
    try:
        result = await get_economy(state.db, state.http, country)
    except Exception:
        log.warning("economy unavailable for %s", country.iso3, exc_info=True)
        raise unavailable("Economía")
    return result.to_response()
