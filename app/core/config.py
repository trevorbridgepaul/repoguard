"""
Application settings.

Reads from environment variables / a .env file via pydantic-settings.
The default database_url matches the docker-compose service hostname
("db") — override it when running outside docker-compose (e.g. against
a locally published Postgres port, or a CI service container).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://repoguard:repoguard@db:5432/repoguard"


settings = Settings()
