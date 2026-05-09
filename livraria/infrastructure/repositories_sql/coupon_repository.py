from __future__ import annotations

from sqlalchemy.orm import Session

from livraria.domain.models.coupon import Coupon
from livraria.domain.ports.repositories import ICouponRepository
from livraria.infrastructure.db.models import CouponRow


class SqlCouponRepository(ICouponRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def find(self, code: str) -> Coupon | None:
        row = self._s.get(CouponRow, code)
        if row is None:
            return None
        return _to_domain(row)

    def save(self, coupon: Coupon) -> None:
        row = self._s.get(CouponRow, coupon.code)
        if row is None:
            self._s.add(
                CouponRow(
                    code=coupon.code,
                    discount_pct=coupon.discount_pct,
                    active=coupon.active,
                    single_use=coupon.single_use,
                    used=coupon.used,
                )
            )
        else:
            row.discount_pct = coupon.discount_pct
            row.active = coupon.active
            row.single_use = coupon.single_use
            row.used = coupon.used

    def mark_used(self, code: str) -> None:
        row = self._s.get(CouponRow, code)
        if row is not None:
            row.used = True


def _to_domain(row: CouponRow) -> Coupon:
    return Coupon(
        code=row.code,
        discount_pct=row.discount_pct,
        active=row.active,
        single_use=row.single_use,
        used=row.used,
    )
