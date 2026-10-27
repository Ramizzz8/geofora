from fastapi import APIRouter, HTTPException, Request

from app.countries import Country

router = APIRouter(prefix="/api")


def get_country_or_404(request: Request, slug: str) -> Country:
    country = request.app.state.countries.by_slug(slug)
    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return country


@router.get("/countries")
def list_countries(request: Request):
    return [
        {"iso3": c.iso3, "slug": c.slug, "name_es": c.name_es}
        for c in request.app.state.countries.all_sorted()
    ]


@router.get("/country/{slug}")
def get_country(request: Request, slug: str):
    return get_country_or_404(request, slug).to_dict()
