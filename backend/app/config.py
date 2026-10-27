from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "geofora.db"
    countries_path: str = str(DATA_DIR / "countries.json")
    lastfm_api_key: str = ""
    deepl_api_key: str = ""
    news_interval_min: int = 45
    enable_scheduler: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
