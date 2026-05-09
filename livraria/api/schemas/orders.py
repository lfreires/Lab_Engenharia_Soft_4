from __future__ import annotations

from pydantic import BaseModel, field_validator

VALID_PAYMENT_METHODS = {"pix", "card", "cash"}


class OrderItemOut(BaseModel):
    book_id: str
    title: str
    quantity: int
    unit_price: float
    subtotal: float


class PaymentOut(BaseModel):
    order_id: str
    amount: float
    method: str
    status: str


class OrderOut(BaseModel):
    id: str
    items: list[OrderItemOut]
    total: float
    status: str
    coupon_code: str | None
    payment: PaymentOut


class CheckoutIn(BaseModel):
    cart_id: str
    payment_method: str = "pix"
    coupon_code: str | None = None

    @field_validator("payment_method")
    @classmethod
    def method_valid(cls, v: str) -> str:
        if v not in VALID_PAYMENT_METHODS:
            raise ValueError(f"Método de pagamento inválido. Use: {VALID_PAYMENT_METHODS}")
        return v


class PreviewDiscountIn(BaseModel):
    cart_total: float
    coupon_code: str


class PreviewDiscountOut(BaseModel):
    discounted_total: float
    savings: float
