# ADR 0002 — Banco de dados

**Status:** Aceito  
**Data:** 2026-05-09  
**Autores:** Lucas Freires

---

## Contexto

A persistência atual é feita em **arquivos TXT (JSON Lines)** no diretório `data/`. Essa abordagem:

- Funciona apenas localmente — **incompatível com Cloud Run**, cujo filesystem é efêmero (container descartado a cada cold start ou scale-to-zero).
- Não suporta concorrência real (múltiplos workers sobrescrevem o mesmo arquivo).
- Não oferece transações verdadeiras (o `TxtUnitOfWork` usa snapshot em memória como workaround).

Para o deploy serverless no GCP precisamos de um banco de dados externo e durável.

**Modelo de dados atual (inferido dos TXT):**

```
users          (username PK, password_hash)
books          (id PK, title, price, stock)
carts          (id PK)
cart_items     (cart_id FK→carts, book_id FK→books, quantity, unit_price)
orders         (id PK, total, status, coupon_code)
order_items    (order_id FK→orders, book_id FK→books, title, quantity, unit_price)
payments       (order_id FK→orders, amount, method, status)
coupons        (code PK, discount_pct, active, single_use, used)
```

O modelo é **claramente relacional**: chaves estrangeiras entre cart↔cart_items, order↔order_items, order↔payment.

**Candidatos avaliados:**

| Critério | Cloud SQL Postgres | Firestore (Native) |
|---|---|---|
| Modelo de dados | Relacional (tabelas, JOINs, FK) | Documento NoSQL (coleções, subcoleções) |
| Serverless | **Não** — instância ligada 24/7 | **Sim** — paga por operação |
| Custo mínimo (dev) | ~US$ 7–10/mês (db-f1-micro, sempre ligado) | ~US$ 0 (free tier: 50k reads/20k writes/dia, 1 GB) |
| Custo prod (baixo tráfego) | US$ 7–15/mês | US$ 0–2/mês |
| Custo prod (alto tráfego) | Previsível (instância fixo + storage) | Imprevisível (cresce por operação) |
| Migração do modelo atual | **Direta** — tabelas mapeiam 1-para-1 | Precisa redesenhar (sem JOINs) |
| ORM / migrations | SQLAlchemy + Alembic | SDK próprio, sem migrations |
| Transações ACID | Sim (nativo) | Sim (transações Firestore, limitado a 500 docs/tx) |
| Integração com Cloud Run | Via Cloud SQL Auth Proxy ou unix socket | Via SDK HTTP |
| Habilidades necessárias | SQL padrão | NoSQL + modelo de dados diferente |

---

## Decisão

**Adotar Cloud SQL Postgres (instância `db-f1-micro`)** para o banco relacional.

Em desenvolvimento local: **SQLite via SQLAlchemy** (mesmo dialect SQL, zero infraestrutura).

### Justificativas

1. **Modelo de dados é relacional** — 8 entidades com FKs explícitas. Reescrevê-las para Firestore exigiria denormalizar (e.g., embutir `order_items` dentro de `orders` como array), o que altera a lógica de reserva de estoque e do `UnitOfWork`. Custo de migração supera o ganho de custo.

2. **Migração direta** — os arquivos TXT já são essencialmente tabelas CSV/JSON. Cada `TxtXxxRepository` mapeia 1-para-1 para uma tabela SQL. A criação de `SqlXxxRepository` será mecânica.

3. **Alembic** — versionamento de schema com `alembic upgrade head` em pipeline CI/CD. Firestore não tem equivalente; evolução de schema é manual e propensa a erros silenciosos.

4. **Custo controlável** — em desenvolvimento, a instância pode ser **parada manualmente** (Cloud Console > Cloud SQL > Stop) para não cobrar enquanto não está em uso. O custo de compute é zero quando parada (só storage, ~US$ 0,10/GB/mês).

5. **SQLAlchemy em modo `dev` usa SQLite** — com `DATABASE_URL=sqlite:///./data/livraria.db` nos testes e dev local, não há necessidade de Docker ou Cloud SQL para desenvolver.

### Por que não Firestore agora

Firestore seria a escolha certa se:
- O modelo fosse predominantemente hierárquico (e.g., carrinho sempre pertence a um usuário e nunca é consultado fora desse contexto).
- O time tivesse familiaridade com NoSQL.
- O objetivo fosse custo **zero** mesmo em produção com baixo volume.

Pode ser avaliado em versão futura se o custo de Cloud SQL se tornar relevante.

---

## Consequências

**Positivas:**
- Zero alteração em domain/services/ports.
- Alembic garante evolução controlada do schema.
- `DATABASE_URL` como env var permite usar SQLite (dev/CI), Postgres local (docker-compose) e Cloud SQL (produção) sem mudar código.
- Transações ACID reais — `SqlUnitOfWork` simplesmente abre/commita/faz rollback de uma `Session`.

**Negativas / atenções:**
- Cloud SQL **não escala a zero** — paga mesmo sem tráfego. Mitigação: parar a instância em dev fora do horário de uso.
- `db-f1-micro` tem 1 vCPU compartilhada e 614 MB RAM — suficiente para tráfego baixo/moderado. Upgrade necessário se o projeto crescer.
- A instância Cloud SQL **não deve ser acessada diretamente** pela Internet. Usar o **Cloud SQL Auth Proxy** (recomendado para Cloud Run via `--add-cloudsql-instances`).

---

## Dependências a adicionar

```
sqlalchemy>=2.0,<3.0
alembic>=1.14
psycopg[binary]>=3.2      # driver Postgres (sync)
# asyncpg>=0.30           # alternativa async — avaliar na fase de otimização
```
