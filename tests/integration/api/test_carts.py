import pytest


@pytest.mark.integration
def test_create_cart_without_token_returns_401(client) -> None:
    resp = client.post("/api/v1/carts")
    assert resp.status_code == 401


@pytest.mark.integration
def test_create_cart_201(client, auth_headers) -> None:
    resp = client.post("/api/v1/carts", headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"]
    assert body["items"] == []
    assert body["total"] == 0.0


@pytest.mark.integration
def test_add_item_to_cart(client, auth_headers) -> None:
    cart_id = client.post("/api/v1/carts", headers=auth_headers).json()["id"]
    resp = client.post(
        f"/api/v1/carts/{cart_id}/items",
        headers=auth_headers,
        json={"book_id": "livro-001", "quantity": 2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert body["total"] == pytest.approx(119.80)


@pytest.mark.integration
def test_get_cart(client, auth_headers) -> None:
    cart_id = client.post("/api/v1/carts", headers=auth_headers).json()["id"]
    resp = client.get(f"/api/v1/carts/{cart_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == cart_id


@pytest.mark.integration
def test_remove_item_from_cart(client, auth_headers) -> None:
    cart_id = client.post("/api/v1/carts", headers=auth_headers).json()["id"]
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        headers=auth_headers,
        json={"book_id": "livro-001", "quantity": 1},
    )
    resp = client.delete(f"/api/v1/carts/{cart_id}/items/livro-001", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["items"] == []
