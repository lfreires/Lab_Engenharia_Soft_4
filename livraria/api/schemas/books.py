from pydantic import BaseModel, field_validator


class BookOut(BaseModel):
    id: str
    title: str
    price: float
    stock: int


class BookCreateIn(BaseModel):
    title: str
    price: float
    stock: int
    id: str | None = None

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero.")
        return v

    @field_validator("stock")
    @classmethod
    def stock_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Estoque não pode ser negativo.")
        return v
