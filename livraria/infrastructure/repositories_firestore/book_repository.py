from __future__ import annotations

from livraria.domain.models.book import Book
from livraria.domain.ports.repositories import IBookRepository
from livraria.infrastructure.repositories_firestore._base import FirestoreRepositoryBase


class FirestoreBookRepository(FirestoreRepositoryBase, IBookRepository):
    _collection = "books"

    def find(self, book_id: str) -> Book:
        ref = self._client.collection(self._collection).document(book_id)
        snap = self._get_doc(ref)
        if not snap.exists:
            raise KeyError(f"Livro '{book_id}' nao encontrado.")
        data = snap.to_dict()
        return Book(
            id=book_id,
            title=str(data["title"]),
            price=float(data["price"]),
            stock=int(data["stock"]),
        )

    def all(self) -> list[Book]:
        query = self._client.collection(self._collection).order_by("title")
        books: list[Book] = []
        for snap in self._stream(query):
            data = snap.to_dict()
            books.append(
                Book(
                    id=snap.id,
                    title=str(data["title"]),
                    price=float(data["price"]),
                    stock=int(data["stock"]),
                )
            )
        return books

    def save(self, book: Book) -> None:
        if book.stock < 0:
            raise ValueError("O estoque nao pode ser negativo.")
        ref = self._client.collection(self._collection).document(book.id)
        self._set_doc(
            ref,
            {
                "title": book.title,
                "price": book.price,
                "stock": book.stock,
            },
        )

    def reserve_stock(self, book_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        ref = self._client.collection(self._collection).document(book_id)
        snap = self._get_doc(ref)
        if not snap.exists:
            raise KeyError(f"Livro '{book_id}' nao encontrado.")
        data = snap.to_dict()
        stock = int(data["stock"])
        if stock < quantity:
            raise ValueError(f"Estoque insuficiente para o livro '{book_id}'.")
        self._update_doc(ref, {"stock": stock - quantity})
