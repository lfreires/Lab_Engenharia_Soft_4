from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from livraria.domain.models.user import User
from livraria.infrastructure.db.models import BookRow, CouponRow, UserRow

if TYPE_CHECKING:
    from google.cloud.firestore import Client


def run_seed(session: Session) -> None:
    """Insere dados iniciais se ainda não existirem (idempotente)."""
    _seed_user(session, username="admin", password="admin123")
    _seed_book(session, book_id="livro-001", title="Clean Code", price=59.90, stock=10)
    _seed_coupon(session, code="DESC10", discount_pct=10.0)
    session.commit()


def _seed_user(session: Session, username: str, password: str) -> None:
    exists = session.query(UserRow).filter_by(username=username).first()
    if exists:
        return
    session.add(
        UserRow(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=User.hash_password(password),
        )
    )


def _seed_book(session: Session, book_id: str, title: str, price: float, stock: int) -> None:
    if session.get(BookRow, book_id):
        return
    session.add(BookRow(id=book_id, title=title, price=price, stock=stock))


def _seed_coupon(session: Session, code: str, discount_pct: float) -> None:
    if session.get(CouponRow, code):
        return
    session.add(
        CouponRow(
            code=code,
            discount_pct=discount_pct,
            active=True,
            single_use=False,
            used=False,
        )
    )


def run_seed_firestore(client: Client) -> None:
    users = client.collection("users")
    books = client.collection("books")
    coupons = client.collection("coupons")

    admin_ref = users.document("admin")
    if not admin_ref.get().exists:
        admin_ref.set(
            {
                "username": "admin",
                "password_hash": User.hash_password("admin123"),
            }
        )

    book_ref = books.document("livro-001")
    if not book_ref.get().exists:
        book_ref.set({"title": "Clean Code", "price": 59.90, "stock": 10})

    coupon_ref = coupons.document("DESC10")
    if not coupon_ref.get().exists:
        coupon_ref.set(
            {
                "discount_pct": 10.0,
                "active": True,
                "single_use": False,
                "used": False,
            }
        )
