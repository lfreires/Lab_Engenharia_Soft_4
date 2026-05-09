from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@lru_cache
def get_engine() -> Engine:
    from livraria.api.settings import get_settings

    settings = get_settings()
    kwargs: dict = {}
    if settings.database_url.startswith("sqlite"):
        # SQLite não suporta múltiplas threads sem esta flag
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(
        settings.database_url,
        echo=(settings.app_env == "local"),
        **kwargs,
    )


@lru_cache
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(get_engine(), autocommit=False, autoflush=False)


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI Depends que fornece uma Session por request.

    Commit automático ao fim do handler (se nenhuma exceção).
    Rollback automático em caso de exceção não tratada.
    Nota: para checkout, o commit já acontece dentro do SqlUnitOfWork;
    o commit aqui é no-op nesse caso.
    """
    factory = _session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
