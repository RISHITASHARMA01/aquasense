from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment / .env file.

    DATABASE_URL falls back to a local SQLite file when unset so the app
    runs out of the box without a Postgres instance for local dev/demo.
    """

    database_url: str = "sqlite:///./aquasense.db"
    secret_key: str = "dev-only-secret-change-me"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    open_meteo_forecast_url: str = "https://api.open-meteo.com/v1/forecast"
    open_meteo_archive_url: str = "https://archive-api.open-meteo.com/v1/archive"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
