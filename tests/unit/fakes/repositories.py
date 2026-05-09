from __future__ import annotations

import uuid

from livraria.domain.models.book import Book
from livraria.domain.models.cart import Cart, CartItem
from livraria.domain.models.coupon import Coupon
from livraria.domain.models.order import Order, OrderItem
from livraria.domain.models.payment import Payment
from livraria.domain.ports.repositories import (
    IBookRepository,
    ICartRepository,
    ICouponRepository,
    IOrderRepository,
    IPaymentRepository,
    IUserRepository,
)
from livraria.domain.ports.unit_of_work import IUnitOfWork


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._db: dict[str, tuple[str, str]] = {}

    def find(self, username: str) -> tuple[str, str] | None:
        return self._db.get(username)

    def exists(self, username: str) -> bool:
        return username in self._db

    def save(self, username: str, password_hash: str) -> None:
        self._db[username] = (username, password_hash)


class FakeBookRepository(IBookRepository):
    def __init__(self, books: list[Book] | None = None) -> None:
        self._db: dict[str, Book] = {b.id: b for b in (books or [])}

    def find(self, book_id: str) -> Book:
        if book_id not in self._db:
            raise KeyError(f"Livro '{book_id}' não encontrado.")
        return self._db[book_id]

    def all(self) -> list[Book]:
        return list(self._db.values())

    def save(self, book: Book) -> None:
        self._db[book.id] = book

    def reserve_stock(self, book_id: str, quantity: int) -> None:
        book = self.find(book_id)
        if book.stock < quantity:
            raise ValueError(f"Estoque insuficiente para '{book.title}'.")
        book.stock -= quantity


class FakeCartRepository(ICartRepository):
    def __init__(self) -> None:
        self._db: dict[str, Cart] = {}

    def create(self) -> Cart:
        cart = Cart(id=str(uuid.uuid4()))
        self._db[cart.id] = cart
        return cart

    def find(self, cart_id: str) -> Cart:
        if cart_id not in self._db:
            raise KeyError(f"Carrinho '{cart_id}' não encontrado.")
        return self._db[cart_id]

    def add_item(self, cart_id: str, book: Book, quantity: int) -> None:
        cart = self.find(cart_id)
        for item in cart.items:
            if item.book_id == book.id:
                item.quantity += quantity
                return
        cart.items.append(
            CartItem(
                book_id=book.id,
                title=book.title,
                quantity=quantity,
                unit_price=book.price,
            )
        )

    def remove_item(self, cart_id: str, book_id: str) -> None:
        cart = self.find(cart_id)
        cart.items = [i for i in cart.items if i.book_id != book_id]

    def clear(self, cart_id: str) -> None:
        self.find(cart_id).items = []


class FakeOrderRepository(IOrderRepository):
    def __init__(self) -> None:
        self.orders: dict[str, dict] = {}
        self.items: dict[str, list[OrderItem]] = {}

    def save(
        self, order_id: str, total: float, status: str, coupon_code: str | None = None
    ) -> None:
        self.orders[order_id] = {"total": total, "status": status, "coupon_code": coupon_code}

    def save_items(self, order_id: str, items: list[OrderItem]) -> None:
        self.items[order_id] = items

    def all(self) -> list[Order]:
        return []


class FakePaymentRepository(IPaymentRepository):
    def __init__(self, *, fail: bool = False) -> None:
        self._db: dict[str, Payment] = {}
        self._fail = fail

    def save(self, payment: Payment) -> None:
        if self._fail:
            raise RuntimeError("gateway indisponível")
        self._db[payment.order_id] = payment


class FakeCouponRepository(ICouponRepository):
    def __init__(self, coupons: list[Coupon] | None = None) -> None:
        self._db: dict[str, Coupon] = {c.code: c for c in (coupons or [])}

    def find(self, code: str) -> Coupon | None:
        return self._db.get(code)

    def save(self, coupon: Coupon) -> None:
        self._db[coupon.code] = coupon

    def mark_used(self, code: str) -> None:
        if code in self._db:
            self._db[code].used = True


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def begin(self) -> None:
        pass

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True
