from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(subject: str, secret: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str, secret: str) -> str:
    """Retorna o subject (username). Lança jwt.ExpiredSignatureError ou jwt.InvalidTokenError."""
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return str(payload["sub"])
