from dataclasses import dataclass


@dataclass
class Article:
    url: str
    title: str
    language: str  # ISO 639-1, o "und" si se desconoce
    domain: str
    source_country: str
    seen_at: float
    score: int = 0  # lugares del país que menciona la noticia: más alto = más relevante
