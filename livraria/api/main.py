from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from livraria.api.middleware.error_handler import add_error_handlers
from livraria.api.routers import auth, books, carts, orders
from livraria.api.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.persistence_backend == "firestore":
        if settings.app_env == "local":
            from livraria.api.seed import run_seed_firestore
            from livraria.infrastructure.firestore.client import get_firestore_client

            run_seed_firestore(get_firestore_client())
        yield
        return

    from livraria.infrastructure.db.engine import _session_factory, get_engine
    from livraria.infrastructure.db.models import Base

    engine = get_engine()

    # create_all apenas para SQLite (dev sem Alembic).
    # Postgres usa `alembic upgrade head` no deploy/docker-compose.
    if settings.app_env == "local" and settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(engine)

    # Seed sempre em local (SQLite ou Postgres após alembic upgrade head)
    if settings.app_env == "local":
        factory = _session_factory()
        session = factory()
        try:
            from livraria.api.seed import run_seed

            run_seed(session)
        finally:
            session.close()

    yield

    engine.dispose()


app = FastAPI(
    title="Livraria API",
    version="0.1.0",
    description=(
        "API REST do sistema de livraria. Documentação completa em /docs (Swagger) ou /redoc."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_error_handlers(app)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(carts.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")


@app.get("/health", tags=["infra"], summary="Health check")
def health() -> dict[str, str]:
    """Endpoint de saúde — usado pelo Cloud Run para health checks."""
    return {"status": "ok"}
