from app.slug import slugify


def test_slugify_strips_accents():
    assert slugify("Afganistán") == "afganistan"


def test_slugify_spaces_to_dashes():
    assert slugify("Costa de Marfil") == "costa-de-marfil"


def test_slugify_trims_and_collapses():
    assert slugify("  São Tomé y Príncipe ") == "sao-tome-y-principe"
