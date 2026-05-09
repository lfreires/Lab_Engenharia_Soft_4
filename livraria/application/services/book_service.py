from __future__ import annotations

from uuid import uuid4

from livraria.domain.models.book import Book
from livraria.domain.ports.repositories import IBookRepository


class BookService:
    def __init__(self, book_repo: IBookRepository) -> None:
        self._repo = book_repo

    def create(self, title: str, price: float, stock: int, book_id: str | None = None) -> Book:
        book = Book(id=book_id or str(uuid4()), title=title, price=price, stock=stock)
        self._repo.save(book)
        return book

    def list_all(self) -> list[Book]:
        return self._repo.all()

    def get_by_id(self, book_id: str) -> Book:
        return self._repo.find(book_id)

    def get_stock(self, book_id: str) -> int:
        return self._repo.find(book_id).stock
