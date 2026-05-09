from __future__ import annotations

import uuid

from livraria.domain.models.book import Book
from livraria.domain.models.cart import Cart, CartItem
from livraria.domain.ports.repositories import ICartRepository
from livraria.infrastructure.repositories_firestore._base import FirestoreRepositoryBase


class FirestoreCartRepository(FirestoreRepositoryBase, ICartRepository):
    _collection = "carts"

    def create(self) -> Cart:
        cart_id = str(uuid.uuid4())
        ref = self._client.collection(self._collection).document(cart_id)
        self._set_doc(ref, {"created": True})
        return Cart(id=cart_id)

    def find(self, cart_id: str) -> Cart:
        cart_ref = self._client.collection(self._collection).document(cart_id)
        cart_snap = self._get_doc(cart_ref)
        if not cart_snap.exists:
            raise KeyError(f"Carrinho '{cart_id}' nao encontrado.")

        items_query = cart_ref.collection("items").order_by("title")
        items = [
            CartItem(
                book_id=snap.id,
                title=str(data["title"]),
                quantity=int(data["quantity"]),
                unit_price=float(data["unit_price"]),
            )
            for snap in self._stream(items_query)
            for data in [snap.to_dict()]
        ]
        return Cart(id=cart_id, items=items)

    def add_item(self, cart_id: str, book: Book, quantity: int) -> None:
        cart_ref = self._client.collection(self._collection).document(cart_id)
        cart_snap = self._get_doc(cart_ref)
        if not cart_snap.exists:
            raise KeyError(f"Carrinho '{cart_id}' nao encontrado.")

        item_ref = cart_ref.collection("items").document(book.id)
        item_snap = self._get_doc(item_ref)
        if item_snap.exists:
            data = item_snap.to_dict()
            new_quantity = int(data["quantity"]) + quantity
        else:
            new_quantity = quantity

        self._set_doc(
            item_ref,
            {
                "title": book.title,
                "quantity": new_quantity,
                "unit_price": book.price,
            },
        )

    def remove_item(self, cart_id: str, book_id: str) -> None:
        item_ref = (
            self._client.collection(self._collection)
            .document(cart_id)
            .collection("items")
            .document(book_id)
        )
        item_snap = self._get_doc(item_ref)
        if item_snap.exists:
            self._delete_doc(item_ref)

    def clear(self, cart_id: str) -> None:
        items_query = (
            self._client.collection(self._collection).document(cart_id).collection("items")
        )
        for snap in self._stream(items_query):
            self._delete_doc(snap.reference)
