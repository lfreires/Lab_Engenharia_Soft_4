from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from livraria.domain.ports.repositories import IUserRepository
from livraria.infrastructure.db.models import UserRow


class SqlUserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def find(self, username: str) -> tuple[str, str] | None:
        row = self._s.execute(
            select(UserRow).where(UserRow.username == username)
        ).scalar_one_or_none()
        if row is None:
            return None
        return (row.username, row.password_hash)

    def exists(self, username: str) -> bool:
        return self.find(username) is not None

    def save(self, username: str, password_hash: str) -> None:
        row = self._s.execute(
            select(UserRow).where(UserRow.username == username)
        ).scalar_one_or_none()
        if row is None:
            self._s.add(
                UserRow(id=str(uuid.uuid4()), username=username, password_hash=password_hash)
            )
        else:
            row.password_hash = password_hash
