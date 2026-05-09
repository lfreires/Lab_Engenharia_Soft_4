from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Ambiente
    app_env: str = "local"
    app_port: int = 8080

    # Banco de dados
    # Fase 2: DATA_DIR aponta para os TXT locais.
    # Fase 5: DATABASE_URL substitui DATA_DIR como fonte de verdade.
    persistence_backend: str = "sql"  # sql | firestore
    data_dir: str = "./data"
    database_url: str = "sqlite:///./data/livraria.db"
    firestore_project_id: str | None = None
    firestore_database: str = "(default)"

    # Auth (JWT) — Fase 6
    jwt_secret: str = "change-me-insecure-dev-only"
    jwt_expires_minutes: int = 60

    # CORS — aceita string separada por vírgula ou lista
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("persistence_backend", mode="before")
    @classmethod
    def parse_backend(cls, v: str) -> str:
        normalized = str(v).strip().lower()
        if normalized not in {"sql", "firestore"}:
            raise ValueError("PERSISTENCE_BACKEND deve ser 'sql' ou 'firestore'.")
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
