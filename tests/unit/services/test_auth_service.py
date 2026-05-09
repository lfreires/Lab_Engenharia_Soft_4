import pytest

from livraria.application.services.auth_service import AuthService
from tests.unit.fakes.repositories import FakeUserRepository


@pytest.fixture
def svc() -> AuthService:
    return AuthService(FakeUserRepository())


@pytest.mark.unit
def test_register_success(svc: AuthService) -> None:
    svc.register("alice", "senha123")
    assert svc.exists("alice")


@pytest.mark.unit
def test_register_duplicate_raises(svc: AuthService) -> None:
    svc.register("alice", "senha123")
    with pytest.raises(ValueError, match="já cadastrado"):
        svc.register("alice", "outrasenha")


@pytest.mark.unit
def test_authenticate_correct_password(svc: AuthService) -> None:
    svc.register("alice", "senha123")
    assert svc.authenticate("alice", "senha123") is True


@pytest.mark.unit
def test_authenticate_wrong_password(svc: AuthService) -> None:
    svc.register("alice", "senha123")
    assert svc.authenticate("alice", "errada") is False


@pytest.mark.unit
def test_authenticate_unknown_user(svc: AuthService) -> None:
    assert svc.authenticate("nobody", "qualquer") is False
