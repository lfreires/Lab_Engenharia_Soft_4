import pytest


@pytest.mark.integration
def test_list_books_returns_seeded_book(client) -> None:
    resp = client.get("/api/v1/books")
    assert resp.status_code == 200
    books = resp.json()
    assert len(books) >= 1
    assert any(b["id"] == "livro-001" for b in books)


@pytest.mark.integration
def test_create_book_201(client) -> None:
    resp = client.post(
        "/api/v1/books",
        json={"id": "novo-livro", "title": "Domain-Driven Design", "price": 89.90, "stock": 3},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == "novo-livro"
    assert body["title"] == "Domain-Driven Design"


@pytest.mark.integration
def test_get_book_by_id(client) -> None:
    resp = client.get("/api/v1/books/livro-001")
    assert resp.status_code == 200
    assert resp.json()["id"] == "livro-001"


@pytest.mark.integration
def test_get_book_not_found_404(client) -> None:
    resp = client.get("/api/v1/books/inexistente")
    assert resp.status_code == 404
