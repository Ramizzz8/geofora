import time
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request

from app.countries import Country
from app.news.store import ArticleOut, heatmap, last_seen, recent_articles

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
    articles, rng = recent_articles(db, country.iso3, time.time(), own_country=country.name_en)
    out = [ArticleOut.untranslated(a) for a in articles]
    return {"range": rng, "articles": [asdict(a) for a in out], "updated_at": last_seen(db)}
