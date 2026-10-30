"""Lo que necesitan los buscadores y las redes sociales: sitemap, robots y metadatos por página.

Los metadatos van en español: cada página tiene una sola URL (con el slug en español) y el
idioma se elige después, en el navegador, donde no llegan quienes no ejecutan JavaScript.
"""
import re
from dataclasses import dataclass
from html import escape
from xml.sax.saxutils import escape as xml_escape

from app.countries import Country

SITE_NAME = "GEOFORA"


@dataclass
class PageMeta:
    title: str
    description: str
    url: str | None = None  # None: la página no se indexa ni tiene URL canónica
    image: str | None = None
    noindex: bool = False


def sitemap_xml(site_url: str, countries: list[Country]) -> str:
    paths = ["/", "/legal"] + [f"/pais/{c.slug}" for c in countries]
    urls = "".join(f"<url><loc>{xml_escape(site_url + p)}</loc></url>" for p in paths)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
    )


def robots_txt(site_url: str) -> str:
    # /api no se bloquea: Google lo necesita para pintar las páginas al ejecutar el JavaScript.
    # Sus respuestas llevan X-Robots-Tag: noindex para que no salgan en los resultados.
    return f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n"


def home_meta(site_url: str) -> PageMeta:
    return PageMeta(
        title=f"{SITE_NAME}: el monitor de actualidad internacional",
        description="Noticias de todo el mundo, país a país y traducidas al español, con la economía, la música y la cultura de cada lugar.",
        url=f"{site_url}/",
    )


def legal_meta(site_url: str) -> PageMeta:
    return PageMeta(
        title=f"Aviso legal y privacidad · {SITE_NAME}",
        description="Aviso legal y política de privacidad de GEOFORA.",
        url=f"{site_url}/legal",
    )


def country_meta(site_url: str, country: Country) -> PageMeta:
    name = country.name_es
    return PageMeta(
        title=f"{name}: noticias, música y economía · {SITE_NAME}",
        description=f"Últimas noticias de {name} traducidas al español, con su economía, música, cultura y fotos, en GEOFORA, el monitor de actualidad internacional.",
        url=f"{site_url}/pais/{country.slug}",
        # las redes sociales no admiten el SVG de la bandera
        image=f"https://flagcdn.com/w640/{country.iso2.lower()}.png" if country.iso2 else None,
    )


def territory_meta(name: str) -> PageMeta:
    # está en el mapa, pero sin ficha: la página solo muestra su nombre
    return PageMeta(title=f"{name} · {SITE_NAME}", description=f"{name} en GEOFORA.", noindex=True)


def not_found_meta() -> PageMeta:
    return PageMeta(title=f"País no encontrado · {SITE_NAME}", description="Este país no existe en GEOFORA.", noindex=True)


def _head_tags(meta: PageMeta) -> str:
    def tag(attr: str, key: str, value: str) -> str:
        return f'<meta {attr}="{key}" content="{escape(value)}" />'

    tags = [f"<title>{escape(meta.title)}</title>", tag("name", "description", meta.description)]
    if meta.noindex:
        tags.append(tag("name", "robots", "noindex"))
    if meta.url:
        tags += [
            f'<link rel="canonical" href="{escape(meta.url)}" />',
            tag("property", "og:type", "website"),
            tag("property", "og:site_name", SITE_NAME),
            tag("property", "og:locale", "es_ES"),
            tag("property", "og:title", meta.title),
            tag("property", "og:description", meta.description),
            tag("property", "og:url", meta.url),
        ]
        if meta.image:
            tags.append(tag("property", "og:image", meta.image))
    return "\n    ".join(tags)


def render_page(template: str, meta: PageMeta) -> str:
    """Sustituye en el index.html compilado el título y la descripción por los de la página."""
    html = re.sub(r'\s*<meta name="description"[^>]*>', "", template, count=1)
    return re.sub(r"<title>.*?</title>", lambda _: _head_tags(meta), html, count=1, flags=re.S)
