# Lab Engenharia Soft 4 - Livraria (Cliente-Servidor)

Projeto academico de uma livraria com arquitetura cliente-servidor:

- Backend: FastAPI (Python), JWT, persistencia SQL/Firestore
- Frontend: React + Vite
- Deploy: GitHub Actions + Google Cloud Run (API) + Vercel (frontend)

## Links do projeto

- Frontend (Vercel): [https://lab-engenharia-soft-4.vercel.app](https://lab-engenharia-soft-4.vercel.app)
- Backend staging (Cloud Run): [https://livraria-api-staging-jar2vmuxea-uc.a.run.app](https://livraria-api-staging-jar2vmuxea-uc.a.run.app)
- Swagger (staging): [https://livraria-api-staging-jar2vmuxea-uc.a.run.app/docs](https://livraria-api-staging-jar2vmuxea-uc.a.run.app/docs)

## Arquitetura

O backend segue Clean Architecture:

- `livraria/domain`: entidades e contratos (ports)
- `livraria/application/services`: casos de uso
- `livraria/infrastructure`: repositorios (SQL e Firestore), UoW, DB
- `livraria/api`: FastAPI, rotas, schemas, dependencia de auth

Frontend:

- `frontend/src/api`: client HTTP e services
- `frontend/src/contexts`: auth/cart state global
- `frontend/src/app/pages`: telas da aplicacao

## Funcionalidades

- Cadastro e login com JWT
- Listagem e cadastro de livros
- Carrinho de compras (criar, adicionar/remover item)
- Preview de desconto por cupom
- Checkout com metodos `pix`, `card`, `cash`
- Baixa de estoque apos pedido

## Estrutura de pastas (resumo)

```text
.
|-- .github/workflows/
|   |-- ci.yml
|   |-- build-image.yml
|   `-- deploy.yml
|-- docs/architecture/
|-- frontend/
|-- livraria/
|-- tests/
|-- Dockerfile
`-- pyproject.toml
```

## Requisitos

- Python 3.12+ (desenvolvimento)
- Node.js 20+ (frontend)
- npm

## Backend local

1. Criar venv e instalar dependencias:

```bash
pip install -e ".[dev]"
```

2. Copiar variaveis:

```bash
cp .env.example .env
```

3. Subir API:

```bash
uvicorn livraria.api.main:app --reload
```

4. Testar:

- Health: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`

## Frontend local

1. Entrar na pasta:

```bash
cd frontend
```

2. Instalar dependencias:

```bash
npm install
```

3. Criar `.env` local (ou ajustar o existente):

```env
VITE_API_BASE_URL=http://localhost:8000
```

4. Rodar:

```bash
npm run dev
```

5. Build:

```bash
npm run build
```

## Variaveis de ambiente

### Backend (`.env`)

Principais campos:

- `APP_ENV=local|test|staging|production`
- `PERSISTENCE_BACKEND=sql|firestore`
- `DATABASE_URL=...` (quando `sql`)
- `FIRESTORE_PROJECT_ID=...` (quando `firestore`)
- `FIRESTORE_DATABASE=...`
- `JWT_SECRET=...`
- `CORS_ALLOWED_ORIGINS=...`

Observacao:

- Para `CORS_ALLOWED_ORIGINS`, em ambiente Cloud Run estamos usando JSON string (lista) para compatibilidade com `pydantic-settings`.

### Frontend (`frontend/.env`)

- `VITE_API_BASE_URL=https://livraria-api-staging-jar2vmuxea-uc.a.run.app`

## Endpoints principais

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/books`
- `POST /api/v1/books`
- `GET /api/v1/books/{id}`
- `POST /api/v1/carts`
- `POST /api/v1/carts/{id}/items`
- `GET /api/v1/carts/{id}`
- `DELETE /api/v1/carts/{id}/items/{book_id}`
- `POST /api/v1/orders/preview-discount`
- `POST /api/v1/orders/checkout`
- `GET /health`

## Qualidade e testes

### Lint e format

```bash
ruff check .
ruff format --check .
```

### Testes

```bash
pytest --cov=livraria --cov-report=term-missing --cov-fail-under=80
```

## Docker

Build:

```bash
docker build -t livraria-api .
```

Run:

```bash
docker run --rm -p 8080:8080 --env-file .env livraria-api
```

## CI/CD

### Workflows

- [ci.yml](.github/workflows/ci.yml)
- [build-image.yml](.github/workflows/build-image.yml)
- [deploy.yml](.github/workflows/deploy.yml)

### Fluxo

1. Push em `main`:
   - roda CI
   - build/push da imagem
   - deploy em `livraria-api-staging`
2. Tag `v*.*.*`:
   - deploy em `livraria-api-prod`

### Secrets/variables no GitHub

- Secret `WIF_PROVIDER`
- Secret `WIF_SERVICE_ACCOUNT`
- Variable (ou Secret) `GCP_PROJECT_ID`

### Pre-requisitos no GCP

- Artifact Registry repo `livraria` em `us-central1`
- Cloud Run habilitado
- Firestore em Native mode
- Secret Manager com `livraria-jwt-secret`
- Service accounts com IAM minimo necessario

## Deploy do frontend (Vercel)

Config recomendada no Vercel:

- Root Directory: `frontend`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`
- Env var: `VITE_API_BASE_URL=https://livraria-api-staging-jar2vmuxea-uc.a.run.app`

## Troubleshooting rapido

### CORS bloqueando no browser

Sintoma:
- erro de preflight e `No 'Access-Control-Allow-Origin' header`

Checklist:
- garantir dominio do frontend em `CORS_ALLOWED_ORIGINS`
- confirmar deploy da revisao nova no Cloud Run

### Container do Cloud Run nao sobe (PORT 8080)

Sintoma:
- `failed to start and listen on the port defined by PORT=8080`

Checklist:
- revisar logs da revisao no Cloud Run
- validar variaveis de ambiente obrigatorias
- validar formato de variaveis complexas (ex.: CORS em JSON string)

## Versionamento (tag e release)

Exemplo para marcar entrega final:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Depois criar a Release no GitHub usando a tag `v1.0.0`.

## Documentacao complementar

- `docs/architecture/cliente-servidor.md`
- `docs/architecture/steps-cliente-servidor.md`
- `docs/architecture/gcp-setup.md`
- `docs/architecture/gcp-iam.md`
- `docs/architecture/gcp-db.md`

## Observacao sobre legado

Existe codigo legado de interface desktop Tkinter (`app.py` e `livraria/views/`) mantido para contexto academico, mas o fluxo oficial da atividade e cliente-servidor via API + frontend web.
