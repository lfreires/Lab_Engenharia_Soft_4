from fastapi import APIRouter, Depends

from livraria.api.deps import CurrentUser, get_checkout_service
from livraria.api.schemas.orders import (
    CheckoutIn,
    OrderItemOut,
    OrderOut,
    PaymentOut,
    PreviewDiscountIn,
    PreviewDiscountOut,
)
from livraria.application.services.checkout_service import CheckoutService
from livraria.domain.models.order import Order

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_schema(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        items=[
            OrderItemOut(
                book_id=item.book_id,
                title=item.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
        total=order.total,
        status=order.status,
        coupon_code=order.coupon_code,
        payment=PaymentOut(
            order_id=order.payment.order_id,
            amount=order.payment.amount,
            method=order.payment.method,
            status=order.payment.status,
        ),
    )


@router.post(
    "/preview-discount",
    response_model=PreviewDiscountOut,
    summary="Calcular desconto do cupom",
    description="Retorna o total com desconto e o valor economizado sem criar o pedido.",
)
def preview_discount(
    body: PreviewDiscountIn,
    _: CurrentUser,
    svc: CheckoutService = Depends(get_checkout_service),
) -> PreviewDiscountOut:
    discounted, savings = svc.preview_discount(body.cart_total, body.coupon_code)
    return PreviewDiscountOut(discounted_total=discounted, savings=savings)


@router.post(
    "/checkout",
    response_model=OrderOut,
    status_code=201,
    summary="Finalizar pedido",
    description=(
        "Executa o checkout completo: reserva estoque, aplica cupom, "
        "registra pedido e pagamento numa transação atômica."
    ),
)
def checkout(
    body: CheckoutIn,
    _: CurrentUser,
    svc: CheckoutService = Depends(get_checkout_service),
) -> OrderOut:
    order = svc.checkout(body.cart_id, body.payment_method, body.coupon_code)
    return _to_schema(order)
