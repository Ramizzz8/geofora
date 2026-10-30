from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "geofora.db"
    countries_path: str = str(DATA_DIR / "countries.json")
    deepl_api_key: str = ""
    news_interval_min: int = 15  # GDELT publica una tanda cada 15 min
    enable_scheduler: bool = True
    # carpeta con la web compilada (frontend/dist); vacía en desarrollo, donde la sirve Vite
    static_dir: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
