from __future__ import annotations

from functools import lru_cache

from google.cloud import firestore

from livraria.api.settings import get_settings


@lru_cache
def get_firestore_client() -> firestore.Client:
    settings = get_settings()
    if settings.firestore_project_id:
        return firestore.Client(
            project=settings.firestore_project_id,
            database=settings.firestore_database,
        )
    return firestore.Client(database=settings.firestore_database)
