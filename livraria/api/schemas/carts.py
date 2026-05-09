from pydantic import BaseModel, field_validator


class CartItemOut(BaseModel):
    book_id: str
    title: str
    quantity: int
    unit_price: float
    subtotal: float


class CartOut(BaseModel):
    id: str
    items: list[CartItemOut]
    total: float


class CartItemAddIn(BaseModel):
    book_id: str
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        return v
