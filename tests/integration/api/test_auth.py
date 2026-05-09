import pytest


@pytest.mark.integration
def test_register_201(client) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "novo", "password": "senha123"},
    )
    assert resp.status_code == 201
    assert resp.json()["message"]


@pytest.mark.integration
def test_register_duplicate_returns_400(client) -> None:
    client.post("/api/v1/auth/register", json={"username": "dup", "password": "abc123"})
    resp = client.post("/api/v1/auth/register", json={"username": "dup", "password": "abc123"})
    assert resp.status_code == 400


@pytest.mark.integration
def test_login_returns_token(client) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.integration
def test_login_wrong_password_401(client) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "errada"},
    )
    assert resp.status_code == 401


@pytest.mark.integration
def test_protected_route_without_token_401(client) -> None:
    resp = client.post("/api/v1/carts")
    assert resp.status_code == 403  # HTTPBearer retorna 403 quando header ausente
