"""
Fixtures de integração.

Estratégia:
- Engine SQLite :memory: criado uma vez por sessão de testes (scope="session").
- Por teste: tabelas populadas via seed, dados limpos após cada teste (truncate).
- Dependência get_db_session sobrescrita para usar o session de teste.
- APP_ENV=test → lifespan não faz create_all nem seed no engine da app.
"""

from __future__ import annotations

import os

# Deve ser definido ANTES de qualquer import do pacote livraria,
# pois main.py chama get_settings() no nível de módulo.
os.environ["APP_ENV"] = "test"
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-32b")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Limpar caches antes de importar o app
from livraria.api.settings import get_settings
from livraria.infrastructure.db.engine import _session_factory, get_engine

get_settings.cache_clear()
get_engine.cache_clear()
_session_factory.cache_clear()

from livraria.api.deps import get_db_session  # noqa: E402
from livraria.api.main import app  # noqa: E402
from livraria.api.seed import run_seed  # noqa: E402
from livraria.infrastructure.db.models import Base  # noqa: E402


@pytest.fixture(scope="session")
def test_engine():
    # StaticPool: todos os sessions compartilham a mesma conexão SQLite,
    # garantindo que o create_all e os testes vejam o mesmo banco :memory:.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    factory = sessionmaker(test_engine, autocommit=False, autoflush=False)
    session = factory()
    run_seed(session)
    yield session
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(delete(table))
    session.commit()
    session.close()


@pytest.fixture
def client(db_session):
    def _override():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
