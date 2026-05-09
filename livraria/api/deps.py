from __future__ import annotations

from typing import Annotated

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from livraria.api.security.jwt import decode_access_token
from livraria.api.settings import Settings, get_settings
from livraria.application.services.auth_service import AuthService
from livraria.application.services.book_service import BookService
from livraria.application.services.cart_service import CartService
from livraria.application.services.checkout_service import CheckoutService
from livraria.infrastructure.db.engine import get_db_session
from livraria.infrastructure.repositories_sql.book_repository import SqlBookRepository
from livraria.infrastructure.repositories_sql.cart_repository import SqlCartRepository
from livraria.infrastructure.repositories_sql.coupon_repository import SqlCouponRepository
from livraria.infrastructure.repositories_sql.order_repository import SqlOrderRepository
from livraria.infrastructure.repositories_sql.payment_repository import SqlPaymentRepository
from livraria.infrastructure.repositories_sql.user_repository import SqlUserRepository
from livraria.infrastructure.unit_of_work_sql import SqlUnitOfWork

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> str:
    """Valida o token JWT e retorna o username. Lança 401 se inválido/expirado."""
    try:
        return decode_access_token(credentials.credentials, settings.jwt_secret)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado.")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")


CurrentUser = Annotated[str, Depends(get_current_user)]


def get_auth_service(
    settings: Settings = Depends(get_settings),
    session=Depends(get_db_session),
) -> AuthService:
    if settings.persistence_backend == "firestore":
        from livraria.infrastructure.firestore.client import get_firestore_client
        from livraria.infrastructure.repositories_firestore import FirestoreUserRepository

        return AuthService(FirestoreUserRepository(get_firestore_client()))
    return AuthService(SqlUserRepository(session))


def get_book_service(
    settings: Settings = Depends(get_settings),
    session=Depends(get_db_session),
) -> BookService:
    if settings.persistence_backend == "firestore":
        from livraria.infrastructure.firestore.client import get_firestore_client
        from livraria.infrastructure.repositories_firestore import FirestoreBookRepository

        return BookService(FirestoreBookRepository(get_firestore_client()))
    return BookService(SqlBookRepository(session))


def get_cart_service(
    settings: Settings = Depends(get_settings),
    session=Depends(get_db_session),
) -> CartService:
    if settings.persistence_backend == "firestore":
        from livraria.infrastructure.firestore.client import get_firestore_client
        from livraria.infrastructure.repositories_firestore import (
            FirestoreBookRepository,
            FirestoreCartRepository,
        )

        client = get_firestore_client()
        return CartService(FirestoreCartRepository(client), FirestoreBookRepository(client))
    return CartService(SqlCartRepository(session), SqlBookRepository(session))


def get_checkout_service(
    settings: Settings = Depends(get_settings),
    session=Depends(get_db_session),
) -> CheckoutService:
    if settings.persistence_backend == "firestore":
        from livraria.infrastructure.firestore.client import get_firestore_client
        from livraria.infrastructure.repositories_firestore import (
            FirestoreBookRepository,
            FirestoreCartRepository,
            FirestoreCouponRepository,
            FirestoreOrderRepository,
            FirestorePaymentRepository,
        )
        from livraria.infrastructure.unit_of_work_firestore import FirestoreUnitOfWork

        client = get_firestore_client()
        uow = FirestoreUnitOfWork(client)
        return CheckoutService(
            book_repo=FirestoreBookRepository(client, uow=uow),
            cart_repo=FirestoreCartRepository(client, uow=uow),
            order_repo=FirestoreOrderRepository(client, uow=uow),
            payment_repo=FirestorePaymentRepository(client, uow=uow),
            coupon_repo=FirestoreCouponRepository(client, uow=uow),
            uow=uow,
        )

    return CheckoutService(
        book_repo=SqlBookRepository(session),
        cart_repo=SqlCartRepository(session),
        order_repo=SqlOrderRepository(session),
        payment_repo=SqlPaymentRepository(session),
        coupon_repo=SqlCouponRepository(session),
        uow=SqlUnitOfWork(session),
    )
