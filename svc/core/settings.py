from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    enable_docs: bool = True

    ndfc_base_url: str = "https://ndfc.example.local"
    ndfc_username: str = "username"
    ndfc_password: str = "password"
    ndfc_timeout_seconds: int = 30
    ndfc_verify_tls: bool = True

    postgres_dsn: str = "postgresql://postgres:postgres@localhost:5432/nco_fabrichub"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
