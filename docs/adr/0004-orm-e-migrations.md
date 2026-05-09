# ADR 0004 — ORM e migrations

**Status:** Aceito  
**Data:** 2026-05-09  
**Autores:** Lucas Freires

---

## Contexto

Com a decisão de usar Postgres (ADR 0002), precisamos definir como o código Python vai interagir com o banco e como o schema vai evoluir ao longo do tempo.

**Restrição fundamental de arquitetura:** os modelos de domínio (`livraria/domain/models/`) são `@dataclass` simples, sem herança de nenhuma classe de framework. Isso é essencial para a Clean Architecture — as entidades não devem saber que existe um banco de dados. Qualquer ORM que exija herança ou decorators nas entidades de domínio viola essa restrição.

**Candidatos avaliados:**

| Critério | SQLAlchemy 2.x (Core/ORM) | SQLModel | Raw SQL (psycopg) |
|---|---|---|---|
| Herança necessária nas entidades | **Não** (usar modelos separados) | Sim (entidades viram `SQLModel`) | Não |
| Clean Architecture | **Compatível** com modelos separados | Viola (funde entidade + ORM + Pydantic) | Compatível |
| Migrations | **Alembic** (mesmo autor, integração nativa) | Alembic (manual) | Manual (scripts SQL) |
| Autogenerate de migrations | **Sim** (a partir dos modelos declarativos) | Sim | Não |
| Async support | Sim (`async_sessionmaker` + `asyncpg`) | Parcial | Sim (`psycopg` async) |
| Maturidade | Alta (20+ anos, v2 estável) | Média (ainda evoluindo) | Alta (psycopg3 estável) |
| Curva de aprendizado | Média | Baixa (mas opiniosa) | Baixa (SQL puro) |
| Quantidade de código nos repos | Moderada | Baixa | Alta (queries manuais) |

---

## Decisão

**Adotar SQLAlchemy 2.x + Alembic.**

Padrão de separação: **dois modelos distintos por entidade** —

```
livraria/domain/models/book.py       → @dataclass Book  (domínio puro)
livraria/infrastructure/db/models.py → BookRow (SQLAlchemy Mapped[...]) 
livraria/infrastructure/repositories_sql/book_repository.py
  → converte BookRow ↔ Book explicitamente
```

### Justificativas

1. **Preserva a Dependency Rule** — `BookRow` (ORM) vive em `infrastructure/`, nunca é importado pelo domínio ou pelos services. A conversão é responsabilidade exclusiva do repositório, que conhece os dois lados.

2. **SQLModel viola a separação** — combinar `SQLModel` + `BaseModel` Pydantic nas entidades de domínio cria acoplamento entre três camadas (ORM, domínio, API schema). Quando o schema da API mudar, não deve ser necessário tocar na entidade de domínio.

3. **Alembic com `autogenerate`** — a partir dos `Mapped[...]` nos modelos ORM, `alembic revision --autogenerate` gera o SQL de migration. Em projetos com versionamento de schema (como este), isso é muito superior a escrever SQL manualmente.

4. **Session como UnitOfWork** — `SqlUnitOfWork` abre uma `Session`, expõe `begin/commit/rollback`, e a passa para todos os repositórios da transação. Isso é um padrão estabelecido em SQLAlchemy 2.x e substitui diretamente o `TxtUnitOfWork` (snapshot em memória).

5. **`DATABASE_URL` controla tudo** — mesma codebase, banco diferente por ambiente:
   - `sqlite:///./data/dev.db` — dev local sem Docker
   - `postgresql+psycopg://...` — Postgres local via docker-compose
   - `postgresql+psycopg://...@/livraria?host=/cloudsql/...` — Cloud SQL via unix socket

### Estrutura de arquivos resultante

```
livraria/
  infrastructure/
    db/
      __init__.py
      engine.py        # cria engine a partir de Settings.database_url
      models.py        # BookRow, UserRow, CartRow, etc. (Mapped[...])
    repositories_sql/
      book_repository.py    # SqlBookRepository(IBookRepository)
      user_repository.py    # SqlUserRepository(IUserRepository)
      cart_repository.py    # SqlCartRepository(ICartRepository)
      order_repository.py   # SqlOrderRepository(IOrderRepository)
      payment_repository.py # SqlPaymentRepository(IPaymentRepository)
      coupon_repository.py  # SqlCouponRepository(ICouponRepository)
    unit_of_work_sql.py     # SqlUnitOfWork(IUnitOfWork)

alembic/
  env.py
  versions/
    0001_initial_schema.py
```

### Exemplo de separação (Book)

```python
# infrastructure/db/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): ...

class BookRow(Base):
    __tablename__ = "books"
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    price: Mapped[float]
    stock: Mapped[int]

# infrastructure/repositories_sql/book_repository.py
from livraria.domain.models.book import Book
from livraria.domain.ports.repositories import IBookRepository
from livraria.infrastructure.db.models import BookRow

class SqlBookRepository(IBookRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find(self, book_id: str) -> Book:
        row = self._session.get(BookRow, book_id)
        if row is None:
            raise KeyError(f"Livro '{book_id}' não encontrado.")
        return Book(id=row.id, title=row.title, price=row.price, stock=row.stock)

    # ...
```

---

## Consequências

**Positivas:**
- Domínio permanece puro — nenhum `import sqlalchemy` em `domain/` ou `application/`.
- Migrations versionadas e reversíveis.
- Flexibilidade de banco por ambiente sem alterar código.
- `SqlUnitOfWork` com transação real elimina o workaround de snapshot em memória.

**Negativas / atenções:**
- Conversão explícita `Row ↔ Domain` é verbosa mas necessária — não usar `model_validate` do Pydantic para isso (os modelos de domínio são `dataclass`, não `BaseModel`).
- `autogenerate` do Alembic não detecta renomeações — sempre revisar o SQL gerado antes de aplicar em produção.
- Em SQLite, alguns tipos e constraints têm comportamento diferente (e.g., `REAL` vs `DOUBLE PRECISION`, sem `ENUM` nativo). Testar migrations em Postgres antes de considerar o schema estável.

---

## Dependências a adicionar

```
sqlalchemy>=2.0,<3.0
alembic>=1.14
psycopg[binary]>=3.2
```
