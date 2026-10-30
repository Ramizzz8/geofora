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
FIPS_URL = "http://data.gdeltproject.org/api/v2/guides/LOOKUP-COUNTRIES.TXT"
ROOT = Path(__file__).resolve().parents[2]
COUNTRIES_OUT = ROOT / "backend" / "data" / "countries.json"
GEO_OUT = ROOT / "frontend" / "public" / "data" / "countries.geojson"
FIPS_OUT = ROOT / "backend" / "data" / "fips.json"

# Natural Earth y REST Countries no siempre usan el mismo código
ALIASES = {"KOS": "UNK"}

# GDELT identifica los países con códigos FIPS 10-4 y nombres propios; estos no
# coinciden por nombre con REST Countries (los islotes y zonas sin país se ignoran)
FIPS_ALIASES = {
    "BF": "BHS", "BK": "BIH", "CF": "COG", "CG": "COD", "EZ": "CZE", "FK": "FLK", "GZ": "PSE",
    "IV": "CIV", "JN": "SJM", "MK": "MKD", "SH": "SHN", "SV": "SJM", "SX": "SGS", "TB": "BLM",
    "TT": "TLS", "VM": "VNM", "VQ": "VIR", "WE": "PSE", "WZ": "SWZ",
}


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
        language_codes=list((r.get("languages") or {}).keys()),
        currency_symbols=[c.get("symbol", "") for c in (r.get("currencies") or {}).values()],
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
        name_en = country.name_en if country else p["NAME"]
        features.append({
            "type": "Feature",
            "properties": {"iso3": code, "name_es": name_es, "name_en": name_en, "slug": slugify(name_es)},
            "geometry": f["geometry"],
        })
    return list(countries.values()), {"type": "FeatureCollection", "features": features}


def build_fips(lookup: str, countries: list[Country]) -> dict[str, str]:
    by_name = {slugify(c.name_en): c.iso3 for c in countries}
    known = {c.iso3 for c in countries}
    out = {}
    for line in lookup.splitlines():
        if "	" not in line:
            continue
        code, name = line.split("	", 1)
        iso3 = FIPS_ALIASES.get(code) or by_name.get(slugify(name))
        if iso3 in known:
            out[code] = iso3
    return out


def main() -> None:
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        rest = client.get(REST_URL).raise_for_status().json()
        geo = client.get(GEO_URL).raise_for_status().json()
        lookup = client.get(FIPS_URL).raise_for_status().text
    countries, geo_out = merge(rest, geo)
    COUNTRIES_OUT.parent.mkdir(parents=True, exist_ok=True)
    GEO_OUT.parent.mkdir(parents=True, exist_ok=True)
    COUNTRIES_OUT.write_text(
        json.dumps([c.to_dict() for c in sorted(countries, key=lambda c: c.iso3)], ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    GEO_OUT.write_text(json.dumps(geo_out, ensure_ascii=False), encoding="utf-8")
    fips = build_fips(lookup, countries)
    FIPS_OUT.write_text(json.dumps(fips, indent=1, sort_keys=True), encoding="utf-8")
    print(f"{len(countries)} países, {len(geo_out['features'])} features, {len(fips)} códigos FIPS")


if __name__ == "__main__":
    main()
