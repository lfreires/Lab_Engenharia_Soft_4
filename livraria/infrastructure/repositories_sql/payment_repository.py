from __future__ import annotations

from sqlalchemy.orm import Session

from livraria.domain.models.payment import Payment
from livraria.domain.ports.repositories import IPaymentRepository
from livraria.infrastructure.db.models import PaymentRow


class SqlPaymentRepository(IPaymentRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def save(self, payment: Payment) -> None:
        self._s.add(
            PaymentRow(
                order_id=payment.order_id,
                amount=payment.amount,
                method=payment.method,
                status=payment.status,
            )
        )
