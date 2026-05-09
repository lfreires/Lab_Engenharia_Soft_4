from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# Modelos SQLAlchemy — camada de infraestrutura APENAS.
# Nunca importar estes modelos em domain/ ou application/.
# A conversão Row ↔ entidade de domínio é responsabilidade exclusiva
# dos repositórios em infrastructure/repositories_sql/.


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BookRow(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)


class CouponRow(Base):
    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    discount_pct: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    single_use: Mapped[bool] = mapped_column(Boolean, default=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class CartRow(Base):
    __tablename__ = "carts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # user_id será populado na Fase 6 (autenticação)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list[CartItemRow]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItemRow(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "book_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[str] = mapped_column(String(36), ForeignKey("carts.id"))
    book_id: Mapped[str] = mapped_column(String(36), ForeignKey("books.id"))
    title: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)

    cart: Mapped[CartRow] = relationship(back_populates="items")


class OrderRow(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # user_id será populado na Fase 6 (autenticação)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    total: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="created")
    coupon_code: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list[OrderItemRow]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    payment: Mapped[PaymentRow | None] = relationship(back_populates="order", uselist=False)


class OrderItemRow(Base):
    __tablename__ = "order_items"
    __table_args__ = (UniqueConstraint("order_id", "book_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"))
    book_id: Mapped[str] = mapped_column(String(36), ForeignKey("books.id"))
    title: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)

    order: Mapped[OrderRow] = relationship(back_populates="items")


class PaymentRow(Base):
    __tablename__ = "payments"

    # PK = order_id: relação 1:1 com orders
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="pending")

    order: Mapped[OrderRow] = relationship(back_populates="payment")
