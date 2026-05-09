from fastapi import APIRouter, Depends, HTTPException

from livraria.api.deps import get_auth_service
from livraria.api.schemas.auth import LoginIn, RegisterIn, TokenOut
from livraria.api.security.jwt import create_access_token
from livraria.api.settings import Settings, get_settings
from livraria.application.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=201,
    summary="Criar conta",
    description="Registra um novo usuário. Retorna 400 se o username já existe.",
)
def register(
    body: RegisterIn,
    svc: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    svc.register(body.username, body.password)
    return {"message": "Usuário criado com sucesso."}


@router.post(
    "/login",
    summary="Autenticar e obter token JWT",
    description=(
        "Valida credenciais e devolve um token JWT. "
        "Use o token no header: `Authorization: Bearer <token>`. "
        "Proteção de rotas via token é ativada na Fase 6."
    ),
)
def login(
    body: LoginIn,
    svc: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> TokenOut:
    if not svc.authenticate(body.username, body.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    token = create_access_token(body.username, settings.jwt_secret, settings.jwt_expires_minutes)
    return TokenOut(access_token=token)
