"""Genera data/countries.json y frontend/public/data/countries.geojson.

Se ejecuta a mano (python -m scripts.build_countries) y su salida se versiona.
"""
import json
from pathlib import Path

import httpx

from app.countries import Country
from app.slug import slugify

REST_URL = (  # la API v3.1 está deprecada; mismos datos, versionados en el repo del proyecto
    "https://gitlab.com/restcountries/restcountries/-/raw/master/src/main/resources/countriesV3.1.json"
)
GEO_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_0_countries.geojson"
)
ROOT = Path(__file__).resolve().parents[2]
COUNTRIES_OUT = ROOT / "backend" / "data" / "countries.json"
GEO_OUT = ROOT / "frontend" / "public" / "data" / "countries.geojson"

# Natural Earth y REST Countries no siempre usan el mismo código
ALIASES = {"KOS": "UNK"}


def to_country(r: dict) -> Country:
    name_es = r.get("translations", {}).get("spa", {}).get("common") or r["name"]["common"]
    return Country(
        iso3=r["cca3"],
        iso2=r.get("cca2", ""),
        slug=slugify(name_es),
        name_es=name_es,
        name_en=r["name"]["common"],
        capital=(r.get("capital") or [None])[0],
        languages=list((r.get("languages") or {}).values()),
        currencies=list((r.get("currencies") or {}).keys()),
        population=r.get("population"),
        timezones=r.get("timezones") or [],
        flag_svg=(r.get("flags") or {}).get("svg"),
    )


def merge(rest: list[dict], geo: dict) -> tuple[list[Country], dict]:
    countries = {c.iso3: c for c in map(to_country, rest)}
    features = []
    for f in geo["features"]:
        p = f["properties"]
        code = p.get("ISO_A3")
        if not code or code == "-99":
            code = p.get("ADM0_A3")
        code = ALIASES.get(code, code)
        country = countries.get(code)
        name_es = country.name_es if country else p["NAME"]
        features.append({
            "type": "Feature",
            "properties": {"iso3": code, "name_es": name_es, "slug": slugify(name_es)},
            "geometry": f["geometry"],
        })
    return list(countries.values()), {"type": "FeatureCollection", "features": features}


def main() -> None:
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        rest = client.get(REST_URL).raise_for_status().json()
        geo = client.get(GEO_URL).raise_for_status().json()
    countries, geo_out = merge(rest, geo)
    COUNTRIES_OUT.parent.mkdir(parents=True, exist_ok=True)
    GEO_OUT.parent.mkdir(parents=True, exist_ok=True)
    COUNTRIES_OUT.write_text(
        json.dumps([c.to_dict() for c in sorted(countries, key=lambda c: c.iso3)], ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    GEO_OUT.write_text(json.dumps(geo_out, ensure_ascii=False), encoding="utf-8")
    print(f"{len(countries)} países, {len(geo_out['features'])} features")


if __name__ == "__main__":
    main()
