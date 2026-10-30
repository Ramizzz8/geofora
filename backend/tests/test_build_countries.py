from scripts.build_countries import merge

REST = [
    {
        "cca3": "AFG", "cca2": "AF",
        "name": {"common": "Afghanistan"},
        "translations": {"spa": {"common": "Afganistán"}},
        "capital": ["Kabul"],
        "languages": {"prs": "Dari", "pus": "Pashto"},
        "currencies": {"AFN": {"name": "Afghan afghani", "symbol": "؋"}},
        "population": 40218234,
        "timezones": ["UTC+04:30"],
        "flags": {"svg": "https://flagcdn.com/af.svg"},
    },
    {
        "cca3": "UNK", "cca2": "XK",
        "name": {"common": "Kosovo"},
        "translations": {"spa": {"common": "Kosovo"}},
        "capital": ["Pristina"], "languages": {"sqi": "Albanian"},
        "currencies": {"EUR": {}}, "population": 1775378,
        "timezones": ["UTC+01:00"], "flags": {"svg": "x.svg"},
    },
]


def feature(iso_a3, adm0_a3, name):
    return {
        "type": "Feature",
        "properties": {"ISO_A3": iso_a3, "ADM0_A3": adm0_a3, "NAME": name},
        "geometry": {"type": "Polygon", "coordinates": []},
    }


GEO = {
    "type": "FeatureCollection",
    "features": [
        feature("AFG", "AFG", "Afghanistan"),
        feature("-99", "KOS", "Kosovo"),
        feature("-99", "SOL", "Somaliland"),
    ],
}


def test_merge_builds_countries_from_rest():
    countries, _ = merge(REST, GEO)
    afg = next(c for c in countries if c.iso3 == "AFG")
    assert afg.slug == "afganistan"
    assert afg.name_es == "Afganistán"
    assert afg.languages == ["Dari", "Pashto"]
    assert afg.language_codes == ["prs", "pus"]
    assert afg.currencies == ["AFN"]
    assert afg.currency_symbols == ["؋"]


def test_merge_uses_adm0_when_iso_missing():
    _, geo = merge(REST, GEO)
    props = [f["properties"] for f in geo["features"]]
    assert {"iso3": "UNK", "name_es": "Kosovo", "name_en": "Kosovo", "slug": "kosovo"} in props


def test_merge_keeps_feature_without_rest_data():
    countries, geo = merge(REST, GEO)
    props = [f["properties"] for f in geo["features"]]
    assert {"iso3": "SOL", "name_es": "Somaliland", "name_en": "Somaliland", "slug": "somaliland"} in props
    assert "SOL" not in {c.iso3 for c in countries}


def test_fips_map_by_name_and_alias():
    from scripts.build_countries import build_fips
    countries, _ = merge(REST, GEO)
    lookup = "AF\tAfghanistan\r\nKV\tKosovo\r\nCF\tCongo\r\nOS\tOceans\r\n"
    rest_cog = REST + [{**REST[0], "cca3": "COG", "name": {"common": "Republic of the Congo"},
                        "translations": {"spa": {"common": "Congo"}}}]
    countries, _ = merge(rest_cog, GEO)
    assert build_fips(lookup, countries) == {"AF": "AFG", "KV": "UNK", "CF": "COG"}
