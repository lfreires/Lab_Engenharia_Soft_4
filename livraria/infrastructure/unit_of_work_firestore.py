from __future__ import annotations

from google.cloud.firestore import Client, Transaction

from livraria.domain.ports.unit_of_work import IUnitOfWork


class FirestoreUnitOfWork(IUnitOfWork):
    """UoW para Firestore com transacao explicita para checkout."""

    def __init__(self, client: Client) -> None:
        self._client = client
        self._transaction: Transaction | None = None

    @property
    def transaction(self) -> Transaction | None:
        return self._transaction

    def begin(self) -> None:
        self._transaction = self._client.transaction()

    def commit(self) -> None:
        if self._transaction is not None:
            self._transaction.commit()
            self._transaction = None

    def rollback(self) -> None:
        if self._transaction is not None:
            self._transaction.rollback()
            self._transaction = None
