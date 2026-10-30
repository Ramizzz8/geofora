"""Indicadores económicos por país: Banco Mundial y, para la deuda pública, FMI."""
import asyncio
import logging
import sqlite3
import time
from datetime import datetime, timezone

import httpx

from app.cache import CacheResult, cached
from app.countries import Country

log = logging.getLogger(__name__)

WB_URL = "https://api.worldbank.org/v2/country"
IMF_DEBT_URL = "https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP"
TTL_S = 7 * 86400  # datos anuales: no cambian a menudo
IMF_TTL_S = 86400
FIRST_YEAR = 2010

# (id, nombre, unidad, indicador del Banco Mundial)
WB_INDICATORS = [
    ("gdp", "PIB", "usd", "NY.GDP.MKTP.CD"),
    ("gdp_pc", "PIB per cápita", "usd", "NY.GDP.PCAP.CD"),
    ("inflation", "Inflación", "pct", "FP.CPI.TOTL.ZG"),
    ("unemployment", "Paro", "pct", "SL.UEM.TOTL.ZS"),
]
DEBT = ("debt", "Deuda pública", "pct_gdp")

# códigos que el Banco Mundial escribe distinto que REST Countries
WB_CODES = {"UNK": "XKX"}


def _indicator(id_: str, label: str, unit: str, series: list[list]) -> dict | None:
    if not series:
        return None
    year, value = series[-1]
    return {"id": id_, "label": label, "unit": unit, "year": year, "value": value, "series": series}


async def _world_bank(client: httpx.AsyncClient, iso3: str, code: str, last_year: int) -> list[list]:
    r = await client.get(f"{WB_URL}/{WB_CODES.get(iso3, iso3)}/indicator/{code}", params={
        "format": "json", "per_page": 100, "date": f"{FIRST_YEAR}:{last_year}",
    })
    r.raise_for_status()
    body = r.json()
    rows = body[1] if len(body) > 1 and body[1] else []  # país sin datos: [{"message": ...}]
    return sorted([int(x["date"]), x["value"]] for x in rows if x["value"] is not None)


async def _imf_debt(conn: sqlite3.Connection, client: httpx.AsyncClient, now) -> dict:
    # el FMI devuelve todos los países en una sola respuesta: se guarda una vez al día
    async def fetch() -> dict:
        r = await client.get(IMF_DEBT_URL)
        r.raise_for_status()
        return r.json()["values"]["GGXWDG_NGDP"]

    return (await cached(conn, "imf:debt", IMF_TTL_S, fetch, now=now)).value


async def get_economy(conn: sqlite3.Connection, client: httpx.AsyncClient, country: Country, now=time.time) -> CacheResult:
    async def fetch() -> dict:
        this_year = datetime.fromtimestamp(now(), tz=timezone.utc).year
        results = await asyncio.gather(
            *(_world_bank(client, country.iso3, code, this_year) for *_, code in WB_INDICATORS),
            _imf_debt(conn, client, now),
            return_exceptions=True,
        )
        if all(isinstance(r, BaseException) for r in results):
            raise RuntimeError("no hay ninguna fuente económica disponible")

        indicators = []
        for (id_, label, unit, _), series in zip(WB_INDICATORS, results):
            if isinstance(series, BaseException):
                log.warning("world bank %s failed for %s: %r", id_, country.iso3, series)
                continue
            indicators.append(_indicator(id_, label, unit, series))

        debt = results[-1]
        if isinstance(debt, BaseException):
            log.warning("imf debt failed: %r", debt)
        else:
            # el FMI incluye estimaciones del año en curso y proyecciones: solo años ya cerrados
            years = debt.get(country.iso3, {})
            series = sorted([int(y), v] for y, v in years.items() if FIRST_YEAR <= int(y) < this_year and v is not None)
            indicators.append(_indicator(*DEBT, series))
        return {"indicators": [i for i in indicators if i]}

    return await cached(conn, f"economy:{country.iso3}", TTL_S, fetch, now=now)
