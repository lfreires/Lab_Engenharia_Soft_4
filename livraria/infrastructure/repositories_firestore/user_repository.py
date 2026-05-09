from __future__ import annotations

from livraria.domain.ports.repositories import IUserRepository
from livraria.infrastructure.repositories_firestore._base import FirestoreRepositoryBase


class FirestoreUserRepository(FirestoreRepositoryBase, IUserRepository):
    _collection = "users"

    def find(self, username: str) -> tuple[str, str] | None:
        ref = self._client.collection(self._collection).document(username)
        snap = self._get_doc(ref)
        if not snap.exists:
            return None
        data = snap.to_dict()
        return (username, str(data["password_hash"]))

    def exists(self, username: str) -> bool:
        return self.find(username) is not None

    def save(self, username: str, password_hash: str) -> None:
        ref = self._client.collection(self._collection).document(username)
        self._set_doc(
            ref,
            {
                "username": username,
                "password_hash": password_hash,
            },
        )
