from __future__ import annotations

from livraria.domain.models.user import User
from livraria.domain.ports.repositories import IUserRepository


class AuthService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._repo = user_repo

    def register(self, username: str, password: str) -> None:
        User.validate(username, password)
        if self._repo.exists(username):
            raise ValueError(f"Usuário '{username}' já cadastrado.")
        self._repo.save(username, User.hash_password(password))

    def authenticate(self, username: str, password: str) -> bool:
        record = self._repo.find(username)
        if record is None:
            return False
        _, stored_hash = record
        return User.verify_password(password, stored_hash)

    def exists(self, username: str) -> bool:
        return self._repo.exists(username)
