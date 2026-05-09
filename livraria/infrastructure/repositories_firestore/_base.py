from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from google.cloud.firestore import Client, DocumentReference

from livraria.infrastructure.unit_of_work_firestore import FirestoreUnitOfWork


class FirestoreRepositoryBase:
    def __init__(self, client: Client, uow: FirestoreUnitOfWork | None = None) -> None:
        self._client = client
        self._uow = uow

    @property
    def _tx(self):  # pragma: no cover - depende de runtime Firestore
        return self._uow.transaction if self._uow is not None else None

    def _get_doc(self, ref: DocumentReference):
        if self._tx is not None:
            return ref.get(transaction=self._tx)
        return ref.get()

    def _set_doc(self, ref: DocumentReference, data: dict[str, Any]) -> None:
        if self._tx is not None:
            self._tx.set(ref, data)
            return
        ref.set(data)

    def _update_doc(self, ref: DocumentReference, data: dict[str, Any]) -> None:
        if self._tx is not None:
            self._tx.update(ref, data)
            return
        ref.update(data)

    def _delete_doc(self, ref: DocumentReference) -> None:
        if self._tx is not None:
            self._tx.delete(ref)
            return
        ref.delete()

    def _stream(self, query) -> Iterable:
        if self._tx is not None:
            return query.stream(transaction=self._tx)
        return query.stream()
