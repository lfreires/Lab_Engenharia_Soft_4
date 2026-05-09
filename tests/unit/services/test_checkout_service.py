import pytest

from livraria.application.services.checkout_service import CheckoutService
from livraria.domain.models.book import Book
from livraria.domain.models.coupon import Coupon
from tests.unit.fakes.repositories import (
    FakeBookRepository,
    FakeCartRepository,
    FakeCouponRepository,
    FakeOrderRepository,
    FakePaymentRepository,
    FakeUnitOfWork,
)

_BOOK = Book(id="b1", title="Clean Code", price=100.0, stock=10)
_COUPON = Coupon(code="DESC10", discount_pct=10.0, active=True, single_use=False, used=False)
_SINGLE_USE_COUPON = Coupon(code="ONE", discount_pct=20.0, active=True, single_use=True, used=False)


def _make_svc(
    books: list[Book] | None = None,
    coupons: list[Coupon] | None = None,
    payment_fail: bool = False,
) -> tuple[CheckoutService, FakeCartRepository, FakeUnitOfWork]:
    book_repo = FakeBookRepository(books or [_BOOK])
    cart_repo = FakeCartRepository()
    order_repo = FakeOrderRepository()
    payment_repo = FakePaymentRepository(fail=payment_fail)
    coupon_repo = FakeCouponRepository(coupons or [_COUPON, _SINGLE_USE_COUPON])
    uow = FakeUnitOfWork()
    svc = CheckoutService(book_repo, cart_repo, order_repo, payment_repo, coupon_repo, uow)
    return svc, cart_repo, uow


def _cart_with_items(cart_repo: FakeCartRepository, quantity: int = 2) -> str:
    cart = cart_repo.create()
    cart_repo.add_item(cart.id, _BOOK, quantity)
    return cart.id


@pytest.mark.unit
def test_checkout_no_coupon() -> None:
    svc, cart_repo, uow = _make_svc()
    cart_id = _cart_with_items(cart_repo, quantity=2)
    order = svc.checkout(cart_id, "pix")
    assert order.total == pytest.approx(200.0)
    assert order.payment.method == "pix"
    assert order.payment.status == "approved"
    assert uow.committed


@pytest.mark.unit
def test_checkout_with_coupon_applies_discount() -> None:
    svc, cart_repo, _ = _make_svc()
    cart_id = _cart_with_items(cart_repo, quantity=2)
    order = svc.checkout(cart_id, "pix", coupon_code="DESC10")
    assert order.total == pytest.approx(180.0)
    assert order.coupon_code == "DESC10"


@pytest.mark.unit
def test_checkout_single_use_coupon_marked_used() -> None:
    svc, cart_repo, _ = _make_svc()
    cart_id = _cart_with_items(cart_repo)
    svc.checkout(cart_id, "pix", coupon_code="ONE")
    # segunda tentativa deve falhar pois o cupom foi marcado como usado
    cart_id2 = _cart_with_items(cart_repo)
    with pytest.raises(ValueError, match="já foi utilizado"):
        svc.checkout(cart_id2, "pix", coupon_code="ONE")


@pytest.mark.unit
def test_checkout_reduces_stock() -> None:
    book = Book(id="b1", title="T", price=50.0, stock=5)
    svc, cart_repo, _ = _make_svc(books=[book])
    cart_id = _cart_with_items(cart_repo, quantity=3)
    svc.checkout(cart_id, "pix")
    assert book.stock == 2


@pytest.mark.unit
def test_checkout_empty_cart_raises() -> None:
    svc, cart_repo, _ = _make_svc()
    cart = cart_repo.create()
    with pytest.raises(ValueError, match="vazio"):
        svc.checkout(cart.id, "pix")


@pytest.mark.unit
def test_checkout_coupon_not_found_raises() -> None:
    svc, cart_repo, _ = _make_svc()
    cart_id = _cart_with_items(cart_repo)
    with pytest.raises(ValueError, match="não encontrado"):
        svc.checkout(cart_id, "pix", coupon_code="INEXISTENTE")


@pytest.mark.unit
def test_checkout_inactive_coupon_raises() -> None:
    inactive = Coupon(code="OFF", discount_pct=5.0, active=False, single_use=False, used=False)
    svc, cart_repo, _ = _make_svc(coupons=[inactive])
    cart_id = _cart_with_items(cart_repo)
    with pytest.raises(ValueError, match="não está ativo"):
        svc.checkout(cart_id, "pix", coupon_code="OFF")


@pytest.mark.unit
def test_checkout_rollback_on_payment_failure() -> None:
    svc, cart_repo, uow = _make_svc(payment_fail=True)
    cart_id = _cart_with_items(cart_repo)
    with pytest.raises(RuntimeError):
        svc.checkout(cart_id, "pix")
    assert uow.rolled_back
    assert not uow.committed


@pytest.mark.unit
def test_preview_discount() -> None:
    svc, _, _ = _make_svc()
    discounted, savings = svc.preview_discount(200.0, "DESC10")
    assert discounted == pytest.approx(180.0)
    assert savings == pytest.approx(20.0)


@pytest.mark.unit
def test_preview_discount_coupon_not_found_raises() -> None:
    svc, _, _ = _make_svc()
    with pytest.raises(ValueError, match="não encontrado"):
        svc.preview_discount(100.0, "NAOEXISTE")
