import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from app.slug import slugify


@dataclass
class Country:
    iso3: str
    iso2: str
    slug: str
    name_es: str
    name_en: str
    capital: str | None
    languages: list[str]
    currencies: list[str]
    population: int | None
    timezones: list[str]
    flag_svg: str | None
    # ISO 639-3, en el mismo orden que languages: el frontend los traduce al español
    language_codes: list[str] = field(default_factory=list)
    # en el mismo orden que currencies
    currency_symbols: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def load_countries(path: str | Path) -> dict[str, Country]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {c["iso3"]: Country(**c) for c in raw}


class CountryIndex:
    def __init__(self, countries: dict[str, Country]):
        self.countries = countries
        self._slugs = {c.slug: c for c in countries.values()}

    def by_slug(self, slug: str) -> Country | None:
        return self._slugs.get(slugify(slug))

    def by_iso3(self, iso3: str) -> Country | None:
        return self.countries.get(iso3)

    def all_sorted(self) -> list[Country]:
        return sorted(self.countries.values(), key=lambda c: slugify(c.name_es))
