from fastapi import APIRouter, Depends

from livraria.api.deps import CurrentUser, get_cart_service
from livraria.api.schemas.carts import CartItemAddIn, CartItemOut, CartOut
from livraria.application.services.cart_service import CartService
from livraria.domain.models.cart import Cart

router = APIRouter(prefix="/carts", tags=["carts"])


def _to_schema(cart: Cart) -> CartOut:
    return CartOut(
        id=cart.id,
        items=[
            CartItemOut(
                book_id=item.book_id,
                title=item.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in cart.items
        ],
        total=cart.total,
    )


@router.post(
    "",
    response_model=CartOut,
    status_code=201,
    summary="Criar carrinho",
    description="Cria um carrinho de compras vazio. Requer autenticação.",
)
def create_cart(
    _: CurrentUser,
    svc: CartService = Depends(get_cart_service),
) -> CartOut:
    return _to_schema(svc.create())


@router.get(
    "/{cart_id}",
    response_model=CartOut,
    summary="Buscar carrinho",
    description="Retorna o carrinho com todos os seus itens e total calculado. Requer autenticação.",  # noqa: E501
)
def get_cart(
    cart_id: str,
    _: CurrentUser,
    svc: CartService = Depends(get_cart_service),
) -> CartOut:
    return _to_schema(svc.get(cart_id))


@router.post(
    "/{cart_id}/items",
    response_model=CartOut,
    summary="Adicionar item ao carrinho",
    description=(
        "Adiciona um livro ao carrinho. Se o livro já existir, incrementa a quantidade. "
        "Retorna 400 se o estoque for insuficiente ou o livro não existir. Requer autenticação."
    ),
)
def add_item(
    cart_id: str,
    body: CartItemAddIn,
    _: CurrentUser,
    svc: CartService = Depends(get_cart_service),
) -> CartOut:
    return _to_schema(svc.add_book(cart_id, body.book_id, body.quantity))


@router.delete(
    "/{cart_id}/items/{book_id}",
    response_model=CartOut,
    summary="Remover item do carrinho",
    description=(
        "Remove um livro do carrinho. Se o livro não estiver no carrinho, "
        "a operação é silenciosa. Requer autenticação."
    ),
)
def remove_item(
    cart_id: str,
    book_id: str,
    _: CurrentUser,
    svc: CartService = Depends(get_cart_service),
) -> CartOut:
    return _to_schema(svc.remove_book(cart_id, book_id))
