# Livraria API - Arquitetura Cliente-Servidor

Projeto de livraria em Python com Clean Architecture, API REST (FastAPI), persistencia configuravel (`sql` ou `firestore`) e deploy serverless no Google Cloud Run.

## Visao Geral

- Backend HTTP: FastAPI
- Arquitetura: Clean Architecture (domain -> application -> infrastructure -> api)
- Persistencia:
- `sql` para SQLite/Postgres
- `firestore` para Cloud Firestore (opcao B do step 11)
- Auth: JWT Bearer token
- Deploy: GitHub Actions + Artifact Registry + Cloud Run

## Estrutura Principal

```text
livraria/
  domain/                  # entidades e ports
  application/services/    # casos de uso
  infrastructure/          # repositorios SQL e Firestore + UoW
  api/                     # FastAPI, routers, schemas, deps, security
docs/
  architecture/            # docs de arquitetura e GCP
tests/
  unit/
  integration/
```

## Requisitos

- Python 3.12+
- pip
- (Opcional) Docker

## Setup Local

1. Criar e ativar ambiente virtual.
2. Instalar dependencias:

```bash
pip install -e ".[dev]"
```

3. Copiar env:

```bash
cp .env.example .env
```

4. Rodar API:

```bash
uvicorn livraria.api.main:app --reload
```

5. Validar:

- Health: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`

## Variaveis de Ambiente

Arquivo base: `.env.example`

Campos principais:

- `APP_ENV=local|staging|production`
- `PERSISTENCE_BACKEND=sql|firestore`
- `DATABASE_URL=...` (quando `sql`)
- `FIRESTORE_PROJECT_ID=...` e `FIRESTORE_DATABASE=...` (quando `firestore`)
- `JWT_SECRET=...`
- `CORS_ALLOWED_ORIGINS=...`

## Endpoints Principais

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/books`
- `POST /api/v1/books`
- `GET /api/v1/books/{id}`
- `POST /api/v1/carts`
- `POST /api/v1/carts/{id}/items`
- `DELETE /api/v1/carts/{id}/items/{book_id}`
- `POST /api/v1/orders/preview-discount`
- `POST /api/v1/orders/checkout`
- `GET /health`

## Testes

```bash
pytest -q
```

## Docker

Build local:

```bash
docker build -t livraria-api .
```

Run local:

```bash
docker run --rm -p 8080:8080 --env-file .env livraria-api
```

Com compose:

```bash
docker compose up --build
```

## Deploy (GCP)

Workflows:

- `.github/workflows/deploy.yml`
- `.github/workflows/build-image.yml`
- `.github/workflows/ci.yml`

Fluxo:

1. Push na `main` -> build/push image e deploy em `livraria-api-staging`
2. Tag `v*.*.*` -> deploy em `livraria-api-prod`

Config necessario no GitHub:

- Secrets: `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`
- Variable (ou Secret): `GCP_PROJECT_ID`

Config necessario no GCP:

- Artifact Registry repo `livraria` em `us-central1`
- Secret Manager: `livraria-jwt-secret`
- Service accounts com IAM minimo (ver docs)
- Firestore habilitado em Native mode (se opcao B)

## Docs de Arquitetura

- `docs/architecture/cliente-servidor.md`
- `docs/architecture/steps-cliente-servidor.md`
- `docs/architecture/gcp-setup.md`
- `docs/architecture/gcp-iam.md`
- `docs/architecture/gcp-db.md`

## Legado

A interface desktop Tkinter antiga continua no repositorio (`app.py` e `livraria/views/`) como referencia academica, mas o caminho principal agora e cliente-servidor via API.
