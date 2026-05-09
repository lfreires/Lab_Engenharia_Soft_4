from __future__ import annotations

from sqlalchemy.orm import Session

from livraria.domain.ports.unit_of_work import IUnitOfWork


class SqlUnitOfWork(IUnitOfWork):
    """UnitOfWork baseado em SQLAlchemy Session.

    A Session já mantém uma transação aberta (autobegin).
    begin()    → no-op: a transação já está ativa desde a primeira operação.
    commit()   → persiste tudo na transação atual.
    rollback() → desfaz tudo desde o último commit/begin.

    IMPORTANTE: todos os repositórios do mesmo request DEVEM compartilhar
    a mesma Session para que o rollback seja efetivo.
    """

    def __init__(self, session: Session) -> None:
        self._s = session

    def begin(self) -> None:
        # Autobegin já garantiu que a transação está aberta.
        # Mantido para compatibilidade com IUnitOfWork.
        pass

    def commit(self) -> None:
        self._s.commit()

    def rollback(self) -> None:
        self._s.rollback()
