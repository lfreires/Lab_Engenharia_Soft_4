from __future__ import annotations

from google.cloud.firestore import Client

from livraria.domain.ports.unit_of_work import IUnitOfWork


class FirestoreUnitOfWork(IUnitOfWork):
    """UoW para Firestore.

    Nota:
    A API de transacoes do client Python exige fluxo callback-based para
    coordenar leituras/escritas e retries automaticamente. O uso atual do
    checkout (begin/commit/rollback imperativo) nao e compativel e causava
    falhas em runtime no Cloud Run.

    Enquanto nao migramos para `run_transaction`, mantemos begin/commit/rollback
    como no-op para preservar a interface do dominio e evitar quebra no fluxo.
    """

    def __init__(self, client: Client) -> None:
        self._client = client
        self._transaction = None

    @property
    def transaction(self):
        return self._transaction

    def begin(self) -> None:
        self._transaction = None

    def commit(self) -> None:
        self._transaction = None

    def rollback(self) -> None:
        self._transaction = None
