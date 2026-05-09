import pytest

from livraria.application.services.cart_service import CartService
from livraria.domain.models.book import Book
from tests.unit.fakes.repositories import FakeBookRepository, FakeCartRepository

_BOOK = Book(id="b1", title="Clean Code", price=59.90, stock=5)


@pytest.fixture
def svc() -> CartService:
    return CartService(FakeCartRepository(), FakeBookRepository([_BOOK]))


@pytest.mark.unit
def test_create_returns_empty_cart(svc: CartService) -> None:
    cart = svc.create()
    assert cart.id
    assert cart.items == []
    assert cart.total == 0.0


@pytest.mark.unit
def test_add_book_creates_item(svc: CartService) -> None:
    cart = svc.create()
    updated = svc.add_book(cart.id, "b1", 2)
    assert len(updated.items) == 1
    assert updated.items[0].quantity == 2
    assert updated.total == pytest.approx(119.80)


@pytest.mark.unit
def test_add_same_book_twice_increments_quantity(svc: CartService) -> None:
    cart = svc.create()
    svc.add_book(cart.id, "b1", 1)
    updated = svc.add_book(cart.id, "b1", 2)
    assert len(updated.items) == 1
    assert updated.items[0].quantity == 3


@pytest.mark.unit
def test_add_exceeds_stock_raises(svc: CartService) -> None:
    cart = svc.create()
    with pytest.raises(ValueError, match="Estoque"):
        svc.add_book(cart.id, "b1", 99)


@pytest.mark.unit
def test_remove_book(svc: CartService) -> None:
    cart = svc.create()
    svc.add_book(cart.id, "b1", 1)
    updated = svc.remove_book(cart.id, "b1")
    assert updated.items == []
