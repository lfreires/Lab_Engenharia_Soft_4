from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CartItem:
    book_id: str
    title: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Cart:
    id: str
    items: list[CartItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def validate_add(self, book_id: str, book_title: str, book_stock: int, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        current = next((i.quantity for i in self.items if i.book_id == book_id), 0)
        if current + quantity > book_stock:
            if current > 0:
                raise ValueError(
                    f"Estoque insuficiente para '{book_title}'. "
                    f"Estoque: {book_stock}, já no carrinho: {current}, "
                    f"disponível para adicionar: {book_stock - current}."
                )
            raise ValueError(
                f"Quantidade indisponível para '{book_title}'. Estoque atual: {book_stock}."
            )
