"""
Application settings.

Reads from environment variables / a .env file via pydantic-settings.
The default database_url matches the docker-compose service hostname
("db") — override it when running outside docker-compose (e.g. against
a locally published Postgres port, or a CI service container).

secret_key ships with an insecure dev-only default so local dev/CI
don't need extra setup — override it with a real secret for any
deployment that isn't just your own machine.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://repoguard:repoguard@db:5432/repoguard"
    secret_key: str = "dev-only-insecure-secret-change-me"
    access_token_expire_minutes: int = 30


settings = Settings()
