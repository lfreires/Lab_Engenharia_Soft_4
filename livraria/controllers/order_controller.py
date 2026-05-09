from livraria.application.services.checkout_service import CheckoutService
from livraria.domain.models.order import Order


class OrderController:
    def __init__(self, service: CheckoutService) -> None:
        self._service = service

    def checkout(
        self, cart_id: str, payment_method: str = "pix", coupon_code: str | None = None
    ) -> Order:
        return self._service.checkout(cart_id, payment_method, coupon_code)

    def preview_discount(self, cart_total: float, coupon_code: str) -> tuple[float, float]:
        return self._service.preview_discount(cart_total, coupon_code)
