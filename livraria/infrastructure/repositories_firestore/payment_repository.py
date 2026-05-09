from __future__ import annotations

from livraria.domain.models.payment import Payment
from livraria.domain.ports.repositories import IPaymentRepository
from livraria.infrastructure.repositories_firestore._base import FirestoreRepositoryBase


class FirestorePaymentRepository(FirestoreRepositoryBase, IPaymentRepository):
    _collection = "payments"

    def save(self, payment: Payment) -> None:
        ref = self._client.collection(self._collection).document(payment.order_id)
        self._set_doc(
            ref,
            {
                "order_id": payment.order_id,
                "amount": payment.amount,
                "method": payment.method,
                "status": payment.status,
            },
        )
