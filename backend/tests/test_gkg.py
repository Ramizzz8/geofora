from datetime import datetime, timezone

import httpx
import pytest
import respx

from app.news.gkg import fetch_gkg, file_url, parse_gkg, slot_floor

FIPS = {"AF": "AFG", "PK": "PAK", "US": "USA", "JA": "JPN", "SP": "ESP"}


def row(url, title, locations, date="20261027161500", domain="x.com", lang=""):
    fields = [""] * 27
    fields[1], fields[3], fields[4], fields[9], fields[25] = date, domain, url, locations, lang
    fields[26] = f"<PAGE_LINKS>a</PAGE_LINKS><PAGE_TITLE>{title}</PAGE_TITLE>"
    return "\t".join(fields)


AF = "1#Afghanistan#AF#AF#33#65#AF"
KABUL = "4#Kabul, Kabul, Afghanistan#AF#AF13#34.5#69.2#-3378435"
PK = "1#Pakistan#PK#PK#30#70#PK"
US = "1#United States#US#US#39#-98#US"


def test_assigns_article_to_main_countries():
    text = row("https://a/1", "Kabul talks", f"{AF};{KABUL};{PK}")
    arts, counts = parse_gkg(text, FIPS)
    # Afganistán aparece en 2 lugares y Pakistán en 1: ambos pasan el umbral de la mitad
    assert set(arts) == {"AFG", "PAK"}
    assert counts == {"AFG": 1, "PAK": 1}
    a = arts["AFG"][0]
    assert a.title == "Kabul talks"
    assert a.language == "en"
    assert a.seen_at == datetime(2026, 10, 27, 16, 15, tzinfo=timezone.utc).timestamp()


def test_minor_mention_is_ignored():
    locs = ";".join([AF, KABUL, "4#Herat, Afghanistan#AF#AF11#34#62#x", "4#Mazar#AF#AF30#36#67#y", US])
    arts, _ = parse_gkg(row("https://a/1", "t", locs), FIPS)
    assert set(arts) == {"AFG"}


def test_at_most_three_countries():
    locs = ";".join(f"1#C{i}#{c}#{c}#0#0#{c}" for i, c in enumerate(["AF", "PK", "US", "JA", "SP"]))
    arts, _ = parse_gkg(row("https://a/1", "t", locs), FIPS)
    assert len(arts) == 3


def test_skips_rows_without_title_or_location_and_unknown_codes():
    text = "\n".join([
        row("https://a/1", "", AF),
        row("https://a/2", "t", ""),
        row("https://a/3", "t", "1#Oceans#OS#OS#0#0#OS"),
        "broken line",
    ])
    assert parse_gkg(text, FIPS) == ({}, {})


def test_translation_language_and_html_entities():
    arts, _ = parse_gkg(row("https://a/1", "V&#xEB;llai &amp; co", AF, lang="srclc:sqi;eng:GT-SQI 1.0"), FIPS)
    a = arts["AFG"][0]
    assert a.language == "sq"
    assert a.title == "Vëllai & co"


def test_score_is_number_of_places_in_that_country():
    arts, _ = parse_gkg(row("https://a/1", "t", f"{AF};{KABUL};{PK}"), FIPS)
    assert arts["AFG"][0].score == 2
    assert arts["PAK"][0].score == 1


def test_cap_keeps_most_relevant():
    many = ";".join(f"4#P{i}#US#US0{i}#0#0#{i}" for i in range(4))
    text = "\n".join([row(f"https://a/{i}", f"t{i}", US) for i in range(6)] + [row("https://a/best", "best", many)])
    arts, _ = parse_gkg(text, FIPS, per_country_cap=5)
    assert arts["USA"][0].url == "https://a/best"


def test_caps_articles_per_country_but_counts_all():
    text = "\n".join(row(f"https://a/{i}", f"t{i}", US) for i in range(8))
    arts, counts = parse_gkg(text, FIPS, per_country_cap=5)
    assert len(arts["USA"]) == 5
    assert counts == {"USA": 8}


def test_file_urls_and_slots():
    ts = datetime(2026, 10, 27, 16, 7, tzinfo=timezone.utc)
    assert slot_floor(ts) == datetime(2026, 10, 27, 16, 0, tzinfo=timezone.utc)
    assert file_url(slot_floor(ts), translation=False) == "http://data.gdeltproject.org/gdeltv2/20261027160000.gkg.csv.zip"
    assert file_url(slot_floor(ts), translation=True) == "http://data.gdeltproject.org/gdeltv2/20261027160000.translation.gkg.csv.zip"


@respx.mock
async def test_fetch_gkg_unzips_in_memory_and_404_is_none():
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("x.gkg.csv", "hola")
    respx.get("http://data.gdeltproject.org/gdeltv2/ok.zip").mock(return_value=httpx.Response(200, content=buf.getvalue()))
    respx.get("http://data.gdeltproject.org/gdeltv2/missing.zip").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        assert await fetch_gkg(client, "http://data.gdeltproject.org/gdeltv2/ok.zip") == "hola"
        assert await fetch_gkg(client, "http://data.gdeltproject.org/gdeltv2/missing.zip") is None
