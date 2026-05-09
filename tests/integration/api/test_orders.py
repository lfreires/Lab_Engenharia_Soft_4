import pytest


@pytest.mark.integration
def test_preview_discount_without_token_returns_403(client) -> None:
    resp = client.post(
        "/api/v1/orders/preview-discount",
        json={"cart_total": 100.0, "coupon_code": "DESC10"},
    )
    assert resp.status_code == 403


@pytest.mark.integration
def test_preview_discount(client, auth_headers) -> None:
    resp = client.post(
        "/api/v1/orders/preview-discount",
        headers=auth_headers,
        json={"cart_total": 200.0, "coupon_code": "DESC10"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["discounted_total"] == pytest.approx(180.0)
    assert body["savings"] == pytest.approx(20.0)


@pytest.mark.integration
def test_checkout_full_flow(client, auth_headers) -> None:
    # Criar carrinho e adicionar item
    cart_id = client.post("/api/v1/carts", headers=auth_headers).json()["id"]
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        headers=auth_headers,
        json={"book_id": "livro-001", "quantity": 2},
    )

    # Checkout sem cupom
    resp = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={"cart_id": cart_id, "payment_method": "pix"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total"] == pytest.approx(119.80)
    assert body["status"] == "created"
    assert body["payment"]["method"] == "pix"
    assert body["payment"]["status"] == "approved"
    assert len(body["items"]) == 1


@pytest.mark.integration
def test_checkout_with_coupon(client, auth_headers) -> None:
    cart_id = client.post("/api/v1/carts", headers=auth_headers).json()["id"]
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        headers=auth_headers,
        json={"book_id": "livro-001", "quantity": 1},
    )
    resp = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={"cart_id": cart_id, "payment_method": "card", "coupon_code": "DESC10"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["coupon_code"] == "DESC10"
    # 59.90 - 10% = 53.91
    assert body["total"] == pytest.approx(53.91)


@pytest.mark.integration
def test_checkout_invalid_payment_method_422(client, auth_headers) -> None:
    cart_id = client.post("/api/v1/carts", headers=auth_headers).json()["id"]
    resp = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={"cart_id": cart_id, "payment_method": "bitcoin"},
    )
    assert resp.status_code == 422
