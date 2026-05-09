from __future__ import annotations

from uuid import uuid4

from livraria.domain.models.order import Order, OrderItem
from livraria.domain.models.payment import Payment
from livraria.domain.ports.repositories import (
    IBookRepository,
    ICartRepository,
    ICouponRepository,
    IOrderRepository,
    IPaymentRepository,
)
from livraria.domain.ports.unit_of_work import IUnitOfWork


class CheckoutService:
    def __init__(
        self,
        book_repo: IBookRepository,
        cart_repo: ICartRepository,
        order_repo: IOrderRepository,
        payment_repo: IPaymentRepository,
        coupon_repo: ICouponRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._books = book_repo
        self._carts = cart_repo
        self._orders = order_repo
        self._payments = payment_repo
        self._coupons = coupon_repo
        self._uow = uow

    def checkout(
        self,
        cart_id: str,
        payment_method: str,
        coupon_code: str | None = None,
    ) -> Order:
        cart = self._carts.find(cart_id)
        if not cart.items:
            raise ValueError("O carrinho está vazio.")

        order_items: list[OrderItem] = [
            OrderItem(
                book_id=item.book_id,
                title=item.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in cart.items
        ]
        raw_total = sum(item.subtotal for item in order_items)

        coupon = None
        if coupon_code:
            coupon = self._coupons.find(coupon_code)
            if coupon is None:
                raise ValueError(f"Cupom '{coupon_code}' não encontrado.")
            coupon.validate()

        total = coupon.apply(raw_total) if coupon else raw_total
        Payment.validate(total, payment_method)

        order_id = str(uuid4())

        try:
            self._uow.begin()
            for item in cart.items:
                self._books.reserve_stock(item.book_id, item.quantity)
            self._orders.save(order_id, total, "created", coupon_code)
            self._orders.save_items(order_id, order_items)
            payment = Payment(
                order_id=order_id, amount=total, method=payment_method, status="approved"
            )
            self._payments.save(payment)
            if coupon and coupon.single_use:
                self._coupons.mark_used(coupon_code)
            self._carts.clear(cart_id)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise

        return Order(
            id=order_id,
            items=order_items,
            total=total,
            payment=payment,
            status="created",
            coupon_code=coupon_code,
        )

    def preview_discount(self, cart_total: float, coupon_code: str) -> tuple[float, float]:
        """Retorna (total_com_desconto, valor_do_desconto). Lança ValueError se cupom inválido."""
        coupon = self._coupons.find(coupon_code)
        if coupon is None:
            raise ValueError(f"Cupom '{coupon_code}' não encontrado.")
        coupon.validate()
        discounted = coupon.apply(cart_total)
        return discounted, round(cart_total - discounted, 2)
