from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from livraria.domain.models.order import Order, OrderItem
from livraria.domain.models.payment import Payment
from livraria.domain.ports.repositories import IOrderRepository
from livraria.infrastructure.db.models import OrderItemRow, OrderRow


class SqlOrderRepository(IOrderRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def save(
        self,
        order_id: str,
        total: float,
        status: str,
        coupon_code: str | None = None,
    ) -> None:
        self._s.add(OrderRow(id=order_id, total=total, status=status, coupon_code=coupon_code))

    def save_items(self, order_id: str, items: list[OrderItem]) -> None:
        for item in items:
            self._s.add(
                OrderItemRow(
                    order_id=order_id,
                    book_id=item.book_id,
                    title=item.title,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )

    def all(self) -> list[Order]:
        rows = (
            self._s.execute(
                select(OrderRow).options(
                    selectinload(OrderRow.items),
                    selectinload(OrderRow.payment),
                )
            )
            .scalars()
            .all()
        )
        return [_to_domain(r) for r in rows if r.payment is not None]


def _to_domain(row: OrderRow) -> Order:
    payment = Payment(
        order_id=row.payment.order_id,
        amount=row.payment.amount,
        method=row.payment.method,
        status=row.payment.status,
    )
    return Order(
        id=row.id,
        items=[
            OrderItem(
                book_id=i.book_id,
                title=i.title,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in row.items
        ],
        total=row.total,
        payment=payment,
        status=row.status,
        coupon_code=row.coupon_code,
    )
