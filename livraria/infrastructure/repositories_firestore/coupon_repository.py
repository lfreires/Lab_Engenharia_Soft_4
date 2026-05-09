from __future__ import annotations

from livraria.domain.models.coupon import Coupon
from livraria.domain.ports.repositories import ICouponRepository
from livraria.infrastructure.repositories_firestore._base import FirestoreRepositoryBase


class FirestoreCouponRepository(FirestoreRepositoryBase, ICouponRepository):
    _collection = "coupons"

    def find(self, code: str) -> Coupon | None:
        ref = self._client.collection(self._collection).document(code)
        snap = self._get_doc(ref)
        if not snap.exists:
            return None
        data = snap.to_dict()
        return Coupon(
            code=code,
            discount_pct=float(data["discount_pct"]),
            active=bool(data["active"]),
            single_use=bool(data["single_use"]),
            used=bool(data["used"]),
        )

    def save(self, coupon: Coupon) -> None:
        ref = self._client.collection(self._collection).document(coupon.code)
        self._set_doc(
            ref,
            {
                "discount_pct": coupon.discount_pct,
                "active": coupon.active,
                "single_use": coupon.single_use,
                "used": coupon.used,
            },
        )

    def mark_used(self, code: str) -> None:
        ref = self._client.collection(self._collection).document(code)
        snap = self._get_doc(ref)
        if snap.exists:
            self._update_doc(ref, {"used": True})
