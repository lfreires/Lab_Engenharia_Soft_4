from __future__ import annotations

from livraria.domain.models.order import Order, OrderItem
from livraria.domain.models.payment import Payment
from livraria.domain.ports.repositories import IOrderRepository
from livraria.infrastructure.repositories_firestore._base import FirestoreRepositoryBase


class FirestoreOrderRepository(FirestoreRepositoryBase, IOrderRepository):
    _collection = "orders"

    def save(
        self,
        order_id: str,
        total: float,
        status: str,
        coupon_code: str | None = None,
    ) -> None:
        ref = self._client.collection(self._collection).document(order_id)
        self._set_doc(
            ref,
            {
                "total": total,
                "status": status,
                "coupon_code": coupon_code,
            },
        )

    def save_items(self, order_id: str, items: list[OrderItem]) -> None:
        order_ref = self._client.collection(self._collection).document(order_id)
        for item in items:
            item_ref = order_ref.collection("items").document(item.book_id)
            self._set_doc(
                item_ref,
                {
                    "title": item.title,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                },
            )

    def all(self) -> list[Order]:
        orders: list[Order] = []
        query = self._client.collection(self._collection)
        for snap in self._stream(query):
            data = snap.to_dict()

            payment_ref = self._client.collection("payments").document(snap.id)
            payment_snap = self._get_doc(payment_ref)
            if not payment_snap.exists:
                continue
            payment_data = payment_snap.to_dict()
            payment = Payment(
                order_id=snap.id,
                amount=float(payment_data["amount"]),
                method=str(payment_data["method"]),
                status=str(payment_data["status"]),
            )

            items_query = snap.reference.collection("items")
            items = [
                OrderItem(
                    book_id=item_snap.id,
                    title=str(item_data["title"]),
                    quantity=int(item_data["quantity"]),
                    unit_price=float(item_data["unit_price"]),
                )
                for item_snap in self._stream(items_query)
                for item_data in [item_snap.to_dict()]
            ]

            orders.append(
                Order(
                    id=snap.id,
                    items=items,
                    total=float(data["total"]),
                    payment=payment,
                    status=str(data["status"]),
                    coupon_code=data.get("coupon_code"),
                )
            )
        return orders
