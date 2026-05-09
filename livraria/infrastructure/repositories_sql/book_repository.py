from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from livraria.domain.models.book import Book
from livraria.domain.ports.repositories import IBookRepository
from livraria.infrastructure.db.models import BookRow


class SqlBookRepository(IBookRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def find(self, book_id: str) -> Book:
        row = self._s.get(BookRow, book_id)
        if row is None:
            raise KeyError(f"Livro '{book_id}' não encontrado.")
        return _to_domain(row)

    def all(self) -> list[Book]:
        rows = self._s.execute(select(BookRow).order_by(BookRow.title)).scalars().all()
        return [_to_domain(r) for r in rows]

    def save(self, book: Book) -> None:
        if book.stock < 0:
            raise ValueError("O estoque não pode ser negativo.")
        row = self._s.get(BookRow, book.id)
        if row is None:
            self._s.add(BookRow(id=book.id, title=book.title, price=book.price, stock=book.stock))
        else:
            row.title = book.title
            row.price = book.price
            row.stock = book.stock

    def reserve_stock(self, book_id: str, quantity: int) -> None:
        # with_for_update() evita race condition em Postgres; no-op no SQLite
        row = self._s.execute(
            select(BookRow).where(BookRow.id == book_id).with_for_update()
        ).scalar_one_or_none()
        if row is None:
            raise KeyError(f"Livro '{book_id}' não encontrado.")
        if row.stock < quantity:
            raise ValueError(f"Estoque insuficiente para o livro '{book_id}'.")
        row.stock -= quantity


def _to_domain(row: BookRow) -> Book:
    return Book(id=row.id, title=row.title, price=row.price, stock=row.stock)
