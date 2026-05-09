from __future__ import annotations

import bcrypt


class User:
    @staticmethod
    def validate(username: str, password: str) -> None:
        if not username or not password:
            raise ValueError("Usuário e senha são obrigatórios.")
        if len(password) < 4:
            raise ValueError("A senha deve ter pelo menos 4 caracteres.")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
