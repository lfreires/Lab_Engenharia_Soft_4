from fastapi import APIRouter, Depends

from livraria.api.deps import get_book_service
from livraria.api.schemas.books import BookCreateIn, BookOut
from livraria.application.services.book_service import BookService
from livraria.domain.models.book import Book

router = APIRouter(prefix="/books", tags=["books"])


def _to_schema(book: Book) -> BookOut:
    return BookOut(id=book.id, title=book.title, price=book.price, stock=book.stock)


@router.get(
    "",
    response_model=list[BookOut],
    summary="Listar livros",
    description="Retorna todos os livros do catálogo com preço e estoque atual. Endpoint público.",
)
def list_books(svc: BookService = Depends(get_book_service)) -> list[BookOut]:
    return [_to_schema(b) for b in svc.list_all()]


@router.post(
    "",
    response_model=BookOut,
    status_code=201,
    summary="Cadastrar livro",
    description=(
        "Cria um novo livro no catálogo. "
        "Retorna 400 se já existir um livro com o mesmo ID. "
        "Proteção de role admin será adicionada em fase futura."
    ),
)
def create_book(
    body: BookCreateIn,
    svc: BookService = Depends(get_book_service),
) -> BookOut:
    book = svc.create(body.title, body.price, body.stock, body.id)
    return _to_schema(book)


@router.get(
    "/{book_id}",
    response_model=BookOut,
    summary="Buscar livro por ID",
    description="Retorna um único livro pelo seu ID. Retorna 404 se não encontrado. Endpoint público.",  # noqa: E501
)
def get_book(
    book_id: str,
    svc: BookService = Depends(get_book_service),
) -> BookOut:
    return _to_schema(svc.get_by_id(book_id))
