import pytest

from livraria.application.services.book_service import BookService
from livraria.domain.models.book import Book
from tests.unit.fakes.repositories import FakeBookRepository


@pytest.fixture
def svc() -> BookService:
    return BookService(FakeBookRepository())


@pytest.mark.unit
def test_create_assigns_uuid(svc: BookService) -> None:
    book = svc.create("Python Fluente", 79.90, 5)
    assert book.id
    assert book.title == "Python Fluente"
    assert book.price == 79.90
    assert book.stock == 5


@pytest.mark.unit
def test_create_with_explicit_id(svc: BookService) -> None:
    book = svc.create("Clean Code", 59.90, 3, book_id="livro-001")
    assert book.id == "livro-001"


@pytest.mark.unit
def test_list_all_returns_all(svc: BookService) -> None:
    svc.create("A", 10.0, 1)
    svc.create("B", 20.0, 2)
    books = svc.list_all()
    assert len(books) == 2


@pytest.mark.unit
def test_get_by_id_found() -> None:
    repo = FakeBookRepository([Book(id="x", title="T", price=1.0, stock=1)])
    svc = BookService(repo)
    book = svc.get_by_id("x")
    assert book.title == "T"


@pytest.mark.unit
def test_get_by_id_not_found(svc: BookService) -> None:
    with pytest.raises(KeyError):
        svc.get_by_id("inexistente")
