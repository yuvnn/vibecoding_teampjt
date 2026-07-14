from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = ""
    database_url: str = "sqlite:///./app/db/localhub.db"
    frontend_origin: str = "http://localhost:5173"
    region: str = "대전/충청권"


@lru_cache
def get_settings() -> Settings:
    return Settings()
