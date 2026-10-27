"""Comprobación manual de la calidad de GDELT con países reales (Tarea 4, paso 5)."""
import asyncio

import httpx
from datetime import datetime

from app.config import Settings
from app.countries import load_countries
from app.http import get_client
from app.news.gdelt import fetch_country_news


async def main(codes=("AFG", "LUX", "SDN")) -> None:
    countries = load_countries(Settings().countries_path)
    async with get_client() as client:
        for i, code in enumerate(codes):
            if i:
                await asyncio.sleep(6)
            for attempt in range(5):
                try:
                    arts = await fetch_country_news(client, countries[code])
                    break
                except (ValueError, httpx.HTTPError):
                    await asyncio.sleep(30)
            else:
                print(f"== {code}: sin respuesta (límite de GDELT)")
                continue
            print(f"== {code}: {len(arts)} artículos")
            for a in arts[:8]:
                when = datetime.fromtimestamp(a.seen_at).strftime("%d/%m %H:%M")
                print(f"  [{a.language}] {when} {a.source_country[:15]:15} {a.title[:90]}")


if __name__ == "__main__":
    asyncio.run(main())
