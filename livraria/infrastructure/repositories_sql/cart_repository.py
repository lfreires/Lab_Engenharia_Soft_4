from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from livraria.domain.models.book import Book
from livraria.domain.models.cart import Cart, CartItem
from livraria.domain.ports.repositories import ICartRepository
from livraria.infrastructure.db.models import CartItemRow, CartRow


class SqlCartRepository(ICartRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def create(self) -> Cart:
        row = CartRow(id=str(uuid.uuid4()))
        self._s.add(row)
        self._s.flush()  # garante que o id está no DB antes de operações subsequentes
        return Cart(id=row.id)

    def find(self, cart_id: str) -> Cart:
        row = self._s.execute(
            select(CartRow).where(CartRow.id == cart_id).options(selectinload(CartRow.items))
        ).scalar_one_or_none()
        if row is None:
            raise KeyError(f"Carrinho '{cart_id}' não encontrado.")
        return _to_domain(row)

    def add_item(self, cart_id: str, book: Book, quantity: int) -> None:
        existing = self._s.execute(
            select(CartItemRow).where(
                CartItemRow.cart_id == cart_id,
                CartItemRow.book_id == book.id,
            )
        ).scalar_one_or_none()
        if existing is not None:
            existing.quantity += quantity
            existing.title = book.title
            existing.unit_price = book.price
        else:
            self._s.add(
                CartItemRow(
                    cart_id=cart_id,
                    book_id=book.id,
                    title=book.title,
                    quantity=quantity,
                    unit_price=book.price,
                )
            )
        self._s.flush()  # torna visível para o find() subsequente (autoflush=False)

    def remove_item(self, cart_id: str, book_id: str) -> None:
        row = self._s.execute(
            select(CartItemRow).where(
                CartItemRow.cart_id == cart_id,
                CartItemRow.book_id == book_id,
            )
        ).scalar_one_or_none()
        if row is not None:
            self._s.delete(row)
            self._s.flush()

    def clear(self, cart_id: str) -> None:
        rows = (
            self._s.execute(select(CartItemRow).where(CartItemRow.cart_id == cart_id))
            .scalars()
            .all()
        )
        for row in rows:
            self._s.delete(row)


def _to_domain(row: CartRow) -> Cart:
    return Cart(
        id=row.id,
        items=[
            CartItem(
                book_id=i.book_id,
                title=i.title,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in row.items
        ],
    )
