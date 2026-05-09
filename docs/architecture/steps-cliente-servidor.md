# Steps de implementação — Arquitetura Cliente-Servidor

Documento complementar a [cliente-servidor.md](cliente-servidor.md). Lista as fases de implementação, agrupadas em ordem de execução. **Foco desta fase do projeto: backend + banco de dados.** Frontend e CI/CD virão depois.

> **Convenção:** cada step traz Objetivo, Arquivos/pastas envolvidos, O que fazer, Critério de conclusão e Risco/atenção.

---

## Fase 1 — Diagnóstico do projeto atual

### Step 1.1 — Inventário do que já existe
- **Objetivo:** mapear o que pode ser reaproveitado e o que falta.
- **Arquivos/pastas:** `livraria/`, `data/`, `app.py`, `example.py`, `README.md`.
- **O que fazer:** ler o documento [cliente-servidor.md](cliente-servidor.md) (seção 3) — o inventário já está consolidado.
- **Critério de conclusão:** time alinhado de que o **domínio + services + ports** serão preservados e que somente **infra + entrypoint HTTP** mudarão.
- **Risco/atenção:** não tentar refatorar o domínio — ele já está limpo. Resistir à tentação de reescrever.

### Step 1.2 — Decisões arquiteturais (ADRs leves)
- **Objetivo:** congelar decisões antes de codar para evitar retrabalho.
- **Arquivos/pastas:** criar `docs/adr/` com arquivos numerados (`0001-framework-http.md`, `0002-banco-de-dados.md`, etc.).
- **O que fazer:** registrar decisão sobre framework (FastAPI vs Flask), banco (Cloud SQL Postgres vs Firestore), auth (JWT próprio vs Firebase Auth), ORM (SQLAlchemy vs raw SQL).
- **Critério de conclusão:** 3–5 ADRs curtos commitados.
- **Risco/atenção:** evitar ADRs longos. Uma página por decisão.

---

## Fase 2 — Definição da arquitetura backend

### Step 2.1 — Escolher framework HTTP
- **Objetivo:** definir a base da API.
- **Arquivos/pastas:** `pyproject.toml` (a criar) ou `requirements.txt`.
- **O que fazer:** recomendado **FastAPI** + **uvicorn** + **pydantic v2**. Adicionar dependências: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`.
- **Critério de conclusão:** `pyproject.toml`/`requirements.txt` criado e instalável.
- **Risco/atenção:** travar versões (`fastapi==0.115.*`) para evitar surpresas em CI.

### Step 2.2 — Definir layout do pacote da API
- **Objetivo:** estrutura clara, alinhada com Clean Architecture já adotada.
- **Arquivos/pastas:**
  ```
  livraria/
    api/
      __init__.py
      main.py              # cria FastAPI app + composition root HTTP
      deps.py              # injeção de dependências (Depends)
      settings.py          # pydantic-settings: lê .env
      schemas/             # Pydantic models (DTOs de entrada/saída)
      routers/
        auth.py
        books.py
        carts.py
        orders.py
      middleware/
        cors.py
        error_handler.py
      security/
        jwt.py
  ```
- **O que fazer:** criar a estrutura vazia (com `__init__.py`).
- **Critério de conclusão:** `uvicorn livraria.api.main:app --reload` sobe sem erro (mesmo com 0 endpoints).
- **Risco/atenção:** **não duplicar** lógica de negócio nos routers — eles devem chamar os services existentes via `Depends`.

### Step 2.3 — Configuração via env
- **Objetivo:** substituir caminhos hard-coded por configuração.
- **Arquivos/pastas:** `livraria/api/settings.py`, `.env.example` (raiz).
- **O que fazer:** classe `Settings(BaseSettings)` com campos: `app_env`, `app_port`, `database_url`, `jwt_secret`, `jwt_expires_minutes`, `cors_allowed_origins`, `log_level`.
- **Critério de conclusão:** `.env.example` commitado; `.env` real **nunca** versionado (cobertos pelo `.gitignore`).
- **Risco/atenção:** nunca colocar valor real de secret em `.env.example`.

---

## Fase 3 — Estruturação da API

### Step 3.1 — Schemas (DTOs)
- **Objetivo:** separar contrato HTTP do modelo de domínio.
- **Arquivos/pastas:** `livraria/api/schemas/{auth,books,carts,orders}.py`.
- **O que fazer:** criar `BookOut`, `BookCreateIn`, `LoginIn`, `LoginOut`, `CartOut`, `CartItemAddIn`, `CheckoutIn`, `OrderOut`, etc., como `BaseModel` Pydantic.
- **Critério de conclusão:** todos os endpoints planejados têm schemas de entrada e saída definidos.
- **Risco/atenção:** **NÃO** retornar entidades de domínio direto na resposta — sempre converter para schema. Evita vazar campos sensíveis.

### Step 3.2 — Routers e endpoints
- **Objetivo:** expor casos de uso via HTTP.
- **Arquivos/pastas:** `livraria/api/routers/`.
- **Mapeamento sugerido:**
  | Método + rota | Service chamado | Notas |
  |---|---|---|
  | `POST /api/v1/auth/register` | `AuthService.register` | retorna 201 |
  | `POST /api/v1/auth/login` | `AuthService.authenticate` | retorna JWT |
  | `GET /api/v1/books` | `BookService.list_all` | público |
  | `POST /api/v1/books` | `BookService.create` | requer auth admin (futuro) |
  | `GET /api/v1/books/{id}` | `BookService` (criar `get_by_id`) | público |
  | `POST /api/v1/carts` | `CartService.create` | requer auth |
  | `POST /api/v1/carts/{id}/items` | `CartService.add_item` | requer auth |
  | `DELETE /api/v1/carts/{id}/items/{book_id}` | `CartService.remove_item` | requer auth |
  | `POST /api/v1/orders/preview-discount` | `CheckoutService.preview_discount` | requer auth |
  | `POST /api/v1/orders/checkout` | `CheckoutService.checkout` | requer auth |
  | `GET /health` | — | sempre 200, usado pelo Cloud Run |
- **Critério de conclusão:** todos os endpoints listados respondem; `/docs` (Swagger) renderiza corretamente.
- **Risco/atenção:** rotas que ainda não tenham service correspondente (ex: `GET /books/{id}`) exigem **adicionar método ao service**, não criar lógica no router.

### Step 3.3 — Tratamento de erros e CORS
- **Objetivo:** respostas consistentes e cliente web habilitado.
- **Arquivos/pastas:** `livraria/api/middleware/`, `livraria/api/main.py`.
- **O que fazer:**
  - Handler global para `ValueError` → HTTP 400 com payload `{"error": "...", "code": "validation_error"}`.
  - Handler para `KeyError` → HTTP 404.
  - `CORSMiddleware` lendo origens permitidas de `Settings`.
- **Critério de conclusão:** chamar com payload inválido retorna 400/422 estruturado, e front em `localhost:3000` consegue chamar.
- **Risco/atenção:** **não usar `allow_origins=["*"]` em produção**.

---

## Fase 4 — Modelagem do banco de dados

### Step 4.1 — Escolher banco e ORM
- **Objetivo:** decidir tecnologia.
- **Arquivos/pastas:** ADR registrando a escolha.
- **O que fazer:** recomendado **Postgres + SQLAlchemy 2.x + Alembic**. Em dev pode usar SQLite (mesmo dialect SQL).
- **Critério de conclusão:** `requirements.txt` inclui `sqlalchemy`, `alembic`, `psycopg[binary]` (ou `asyncpg` se for usar async).
- **Risco/atenção:** se escolher Firestore, este step muda completamente — substituir SQLAlchemy/Alembic por `google-cloud-firestore`.

### Step 4.2 — Modelar tabelas
- **Objetivo:** mapear entidades atuais para schema relacional.
- **Arquivos/pastas:** `livraria/infrastructure/db/models.py` (modelos SQLAlchemy, **separados** dos modelos de domínio).
- **Tabelas sugeridas:**
  - `users` (id, username UNIQUE, password_hash, created_at)
  - `books` (id, title, price, stock)
  - `carts` (id, user_id FK, created_at)
  - `cart_items` (cart_id FK, book_id FK, quantity, unit_price, PK composta)
  - `orders` (id, user_id FK, total, status, coupon_code, created_at)
  - `order_items` (order_id FK, book_id FK, title, quantity, unit_price)
  - `payments` (order_id FK, amount, method, status)
  - `coupons` (code PK, discount_pct, active, single_use, used)
- **Critério de conclusão:** modelos definidos e o esquema gerado equivale ao formato hoje em `data/*.txt`.
- **Risco/atenção:** **não fundir** modelo SQLAlchemy com entidade de domínio — manter conversão explícita no repositório.

### Step 4.3 — Migrations Alembic
- **Objetivo:** evolução versionada do schema.
- **Arquivos/pastas:** `alembic.ini`, `alembic/env.py`, `alembic/versions/`.
- **O que fazer:** `alembic init alembic` → configurar `env.py` para ler `DATABASE_URL` da `Settings` → `alembic revision --autogenerate -m "initial schema"`.
- **Critério de conclusão:** `alembic upgrade head` cria todas as tabelas em DB vazio.
- **Risco/atenção:** revisar SQL gerado pelo autogenerate antes de aplicar — ele costuma errar em índices e tipos custom.

---

## Fase 5 — Integração backend → banco

### Step 5.1 — Implementar repositórios SQL
- **Objetivo:** trocar a infra de TXT por SQL **sem tocar nos services**.
- **Arquivos/pastas:** `livraria/infrastructure/repositories_sql/{book,cart,order,payment,user,coupon}_repository.py`.
- **O que fazer:** cada classe implementa o port correspondente (`IBookRepository`, etc.) usando `Session` do SQLAlchemy. Conversão entre row → entidade de domínio fica nesses arquivos.
- **Critério de conclusão:** todos os ports têm implementação SQL e os services rodam contra Postgres sem alteração.
- **Risco/atenção:** atenção a transações — usar `Session` corretamente, sem leaks.

### Step 5.2 — `SqlUnitOfWork`
- **Objetivo:** transação real, substituindo o snapshot em memória.
- **Arquivos/pastas:** `livraria/infrastructure/unit_of_work_sql.py`.
- **O que fazer:** classe que abre `Session`, expõe `begin/commit/rollback` e injeta a mesma session nos repositórios para que tudo participe da mesma transação.
- **Critério de conclusão:** `CheckoutService.checkout` roda contra DB e respeita rollback em caso de exceção.
- **Risco/atenção:** garantir que **todos** os repositórios usam a session do UoW durante uma operação transacional. Caso contrário o rollback não funciona.

### Step 5.3 — Composition root para a API
- **Objetivo:** montar o grafo HTTP separadamente do `app.py` Tkinter.
- **Arquivos/pastas:** `livraria/api/main.py`, `livraria/api/deps.py`.
- **O que fazer:** em `deps.py`, criar funções `get_book_service`, `get_checkout_service`, etc., que devolvem instâncias com repositórios SQL injetados. Usar `Depends` nos routers.
- **Critério de conclusão:** API sobe e atende requests reais persistindo em Postgres.
- **Risco/atenção:** lifecycle do `engine`/`SessionLocal` deve ser **um por processo**, não por request.

---

## Fase 6 — Variáveis de ambiente e segurança

### Step 6.1 — `.env.example` completo
- **Objetivo:** documentar configuração mínima.
- **Arquivos/pastas:** `.env.example` na raiz.
- **O que fazer:** ver lista em [cliente-servidor.md](cliente-servidor.md#44-variáveis-de-ambiente).
- **Critério de conclusão:** `cp .env.example .env && python -m uvicorn livraria.api.main:app` funciona após preencher campos obrigatórios.
- **Risco/atenção:** revisar o `.gitignore` para confirmar que `.env` está ignorado e `.env.example` **não** está.

### Step 6.2 — Hash de senha seguro
- **Objetivo:** trocar SHA-1/MD5 por algoritmo adequado.
- **Arquivos/pastas:** `livraria/domain/models/user.py`.
- **O que fazer:** usar `bcrypt` ou `argon2-cffi`. Cuidado: **migrar usuários existentes** — solução típica é exigir reset na primeira autenticação após o upgrade.
- **Critério de conclusão:** registros novos usam o algoritmo escolhido; testes passam.
- **Risco/atenção:** mudança quebra hashes antigos; coordenar com Step 4.2 (schema do banco).

### Step 6.3 — JWT
- **Objetivo:** autenticação stateless para a API.
- **Arquivos/pastas:** `livraria/api/security/jwt.py`, `livraria/api/deps.py` (com dependência `get_current_user`).
- **O que fazer:** emitir JWT no login (`pyjwt` ou `python-jose`); validar no `Depends` em rotas protegidas.
- **Critério de conclusão:** rotas protegidas exigem `Authorization: Bearer <token>` e respondem 401 sem token válido.
- **Risco/atenção:** `JWT_SECRET` **deve** vir de Secret Manager em produção, nunca de `.env` commitado.

---

## Fase 7 — Preparação para frontend futuro

### Step 7.1 — Documentar contrato (OpenAPI)
- **Objetivo:** dar ao futuro time de frontend uma referência sólida.
- **Arquivos/pastas:** documentação gerada automaticamente em `/docs` e `/openapi.json` (FastAPI).
- **O que fazer:** garantir que todos os endpoints têm `summary`, `description`, `response_model` e exemplos.
- **Critério de conclusão:** `openapi.json` exportado e versionado em `docs/api/openapi.json` (snapshot por release).
- **Risco/atenção:** mudança breaking de schema sem versionar quebra clientes.

### Step 7.2 — CORS configurado para os domínios do frontend
- **Objetivo:** evitar bloqueio do navegador.
- **Arquivos/pastas:** `livraria/api/middleware/cors.py`.
- **O que fazer:** ler `CORS_ALLOWED_ORIGINS` da `Settings` (lista). Local: `http://localhost:3000`. Produção: domínios reais.
- **Critério de conclusão:** browser consegue chamar a API a partir do domínio configurado.
- **Risco/atenção:** atenção a `allow_credentials=True` + `allow_origins=["*"]` (proibido pelo browser).

### Step 7.3 — Política de auth para o frontend
- **Objetivo:** alinhar onde o token é guardado.
- **Arquivos/pastas:** ADR (`docs/adr/000X-auth-token-storage.md`).
- **O que fazer:** decidir entre cookie httpOnly (mais seguro contra XSS) ou localStorage (mais simples). Recomendado **cookie httpOnly + SameSite=Lax**.
- **Critério de conclusão:** ADR escrito; backend preparado para emitir cookie se for o caso.
- **Risco/atenção:** cookie httpOnly exige CSRF token em mutações — incluir no plano.

---

## Fase 8 — Testes da API

### Step 8.1 — Testes unitários dos services
- **Objetivo:** garantir que a lógica de negócio continua correta.
- **Arquivos/pastas:** `tests/unit/services/test_*.py`.
- **O que fazer:** usar **fakes** dos ports (in-memory dicts) — não mockar com `unittest.mock`. Testar `AuthService`, `BookService`, `CartService`, `CheckoutService` (especialmente cupom + rollback).
- **Critério de conclusão:** cobertura ≥ 80% nos services.
- **Risco/atenção:** **não usar TXT real** nos testes — instabilidade de I/O.

### Step 8.2 — Testes de integração da API
- **Objetivo:** validar contrato HTTP end-to-end.
- **Arquivos/pastas:** `tests/integration/api/test_*.py`.
- **O que fazer:** usar `TestClient` do FastAPI + SQLite em memória ou Postgres efêmero (testcontainers). Cobrir caminho feliz e principais erros.
- **Critério de conclusão:** suite roda em < 30s e cobre todos os endpoints.
- **Risco/atenção:** isolar fixtures por teste — não compartilhar estado de DB entre testes.

### Step 8.3 — `pytest.ini` / `pyproject.toml` para testes
- **Objetivo:** comando único para rodar tudo.
- **Arquivos/pastas:** `pyproject.toml` (seção `[tool.pytest.ini_options]`).
- **O que fazer:** configurar `testpaths`, `addopts = "-v --strict-markers"`, marcadores `unit`/`integration`.
- **Critério de conclusão:** `pytest` roda toda a suite localmente.
- **Risco/atenção:** sem testes os steps anteriores não têm como ser validados em CI.

---

## Fase 9 — Dockerização

### Step 9.1 — `Dockerfile` da API
- **Objetivo:** imagem leve para Cloud Run.
- **Arquivos/pastas:** `Dockerfile`, `.dockerignore`.
- **O que fazer:** **multi-stage**: stage builder com `pip wheel`, stage final em `python:3.12-slim`. Rodar como user não-root. `CMD ["uvicorn", "livraria.api.main:app", "--host", "0.0.0.0", "--port", "8080"]`.
- **Critério de conclusão:** `docker build -t livraria-api .` produz imagem < 200 MB; container atende em `:8080`.
- **Risco/atenção:** Cloud Run espera a app escutar em `$PORT` (default 8080) — usar a env var.

### Step 9.2 — `docker-compose.yml` para dev local
- **Objetivo:** ambiente local com Postgres sem instalar na máquina.
- **Arquivos/pastas:** `docker-compose.yml`.
- **O que fazer:** dois serviços — `api` (build local) e `db` (image `postgres:16`). Volume nomeado para persistir DB. Healthcheck no DB.
- **Critério de conclusão:** `docker compose up` sobe API + Postgres; migrations rodam no boot da API.
- **Risco/atenção:** não deixar `POSTGRES_PASSWORD` hard-coded — vir de `.env`.

### Step 9.3 — `.dockerignore`
- **Objetivo:** evitar que `data/`, `.venv`, `.git`, etc. inflem a imagem.
- **Arquivos/pastas:** `.dockerignore`.
- **O que fazer:** padrão do projeto (similar ao `.gitignore`, mas mais agressivo: ignora `tests/`, `docs/`, `*.md`).
- **Critério de conclusão:** imagem < 200 MB confirmado.
- **Risco/atenção:** não ignorar `pyproject.toml`/`requirements.txt` — sem eles o build quebra.

---

## Fase 10 — Preparação para CI/CD no GCP

### Step 10.1 — Workflow básico (lint + test) no GitHub Actions
- **Objetivo:** validar PRs.
- **Arquivos/pastas:** `.github/workflows/ci.yml`.
- **O que fazer:** trigger em `push` e `pull_request`. Steps: checkout → setup Python → instalar deps → `ruff check` → `pytest`.
- **Critério de conclusão:** pipeline verde em PR fictício.
- **Risco/atenção:** não exigir secrets do GCP nesta etapa — apenas testes.

### Step 10.2 — Workflow de build de imagem
- **Objetivo:** preparar deploy futuro.
- **Arquivos/pastas:** `.github/workflows/build-image.yml`.
- **O que fazer:** em push para `main`, build da imagem Docker e push para **Artifact Registry** (autenticação via Workload Identity Federation, **sem chave JSON**).
- **Critério de conclusão:** imagem aparece em `us-central1-docker.pkg.dev/<project>/livraria/api:<sha>`.
- **Risco/atenção:** **não** usar Service Account Key JSON — usar Workload Identity Federation para evitar chave estática.

### Step 10.3 — Service accounts e IAM mínimos
- **Objetivo:** princípio do menor privilégio.
- **Arquivos/pastas:** `docs/architecture/gcp-iam.md` (a criar quando for implementar).
- **O que fazer:** criar SA `livraria-api-runtime` com roles: `roles/cloudsql.client`, `roles/secretmanager.secretAccessor`, `roles/logging.logWriter`. Criar SA `livraria-ci-deployer` com roles: `roles/artifactregistry.writer`, `roles/run.admin`, `roles/iam.serviceAccountUser`.
- **Critério de conclusão:** documentado; aplicação efetiva fica para quando o GCP for provisionado.
- **Risco/atenção:** **não usar `roles/owner`** ou `roles/editor` na SA da API.

---

## Fase 11 — Preparação para deploy serverless no GCP

### Step 11.1 — Provisionar projeto e billing alerts (sem criar recursos pagos ainda)
- **Objetivo:** preparar a casa antes de mobiliar.
- **Arquivos/pastas:** documentação em `docs/architecture/gcp-setup.md` (a criar).
- **O que fazer:** criar projeto GCP, ativar APIs (Cloud Run, Artifact Registry, Cloud SQL Admin, Secret Manager, Cloud Build), configurar **billing alert** em US$ 5/10/20.
- **Critério de conclusão:** projeto criado, alertas configurados, **nenhum recurso pago em execução**.
- **Risco/atenção:** ativar APIs **não** custa, mas configurações default às vezes provisionam recursos. Conferir Cloud Console > Billing após cada ativação.

### Step 11.2 — Workflow de deploy para Cloud Run
- **Objetivo:** entregar a API em ambiente serverless.
- **Arquivos/pastas:** `.github/workflows/deploy.yml`.
- **O que fazer:** após build/push da imagem, `gcloud run deploy livraria-api --image ... --region us-central1 --allow-unauthenticated --min-instances 0 --max-instances 5 --concurrency 80 --memory 512Mi --cpu 1`.
- **Critério de conclusão:** deploy automático em push para `main` (staging) e em tag (produção).
- **Risco/atenção:** `--min-instances 0` é o que zera o custo em ociosidade. **Não** colocar `--min-instances 1` sem necessidade.

### Step 11.3 — Banco de dados gerenciado
- **Objetivo:** persistência durável.
- **Arquivos/pastas:** documentação `docs/architecture/gcp-db.md` (a criar).
- **O que fazer:**
  - **Opção A (Postgres):** Cloud SQL Postgres `db-f1-micro`, conexão via Cloud SQL Auth Proxy ou conector unix-socket do Cloud Run. Em dev, **parar a instância** quando não estiver em uso.
  - **Opção B (Firestore):** ativar Firestore em modo Native, usar `google-cloud-firestore` SDK. Reescrever apenas `repositories_sql/` por `repositories_firestore/`.
- **Critério de conclusão:** API em Cloud Run consegue ler/escrever no banco.
- **Risco/atenção:** Cloud SQL **não é serverless puro** — paga 24/7 mesmo ocioso. Avaliar Firestore se prioridade for custo zero em ociosidade.

### Step 11.4 — Secrets em Secret Manager
- **Objetivo:** tirar credenciais do `.env` em produção.
- **Arquivos/pastas:** workflow de deploy.
- **O que fazer:** criar secrets `livraria-jwt-secret`, `livraria-db-url`. Montar no Cloud Run via `--update-secrets JWT_SECRET=livraria-jwt-secret:latest`.
- **Critério de conclusão:** API em produção lê secrets sem `.env` montado.
- **Risco/atenção:** dar à SA da API **só** `roles/secretmanager.secretAccessor` nesses secrets específicos, não no projeto inteiro.

---

## Fase 12 — Deploy futuro no Google Cloud Platform

### Step 12.1 — Deploy inicial em staging
- **Objetivo:** primeiro deploy real.
- **O que fazer:** acionar o workflow de deploy contra o serviço `livraria-api-staging`. Validar `/health` e endpoints principais via Swagger remoto.
- **Critério de conclusão:** URL `https://livraria-api-staging-xxx.run.app/docs` acessível.
- **Risco/atenção:** confirmar que `min-instances=0` e que a instância **escala a zero** após alguns minutos sem tráfego (ver Cloud Run > Metrics).

### Step 12.2 — Frontend hosting
- **Objetivo:** servir o frontend (quando existir) com custo mínimo.
- **O que fazer:** quando o frontend for criado, hospedar em **Firebase Hosting** ou **Cloud Storage estático + Cloud CDN**. Ambos têm free tier suficiente para projetos pequenos.
- **Critério de conclusão:** frontend em domínio próprio, HTTPS automático, chamando a API.
- **Risco/atenção:** configurar CORS no backend antes; configurar CSP que permita o domínio da API.

### Step 12.3 — Promoção para produção
- **Objetivo:** estabilidade.
- **O que fazer:** definir gating: tag `v*.*.*` aciona deploy em prod. Rodar smoke tests pós-deploy.
- **Critério de conclusão:** deploy de produção sem downtime perceptível.
- **Risco/atenção:** Cloud Run faz deploy blue/green automaticamente, mas migrations de banco precisam ser **backwards-compatible** (expand/contract).

### Step 12.4 — Observabilidade e alertas
- **Objetivo:** saber quando algo quebra.
- **O que fazer:** Cloud Logging já vem ligado; criar alertas em **Cloud Monitoring** para: erro 5xx > 1% por 5 min, latência p95 > 1s, billing > US$ X.
- **Critério de conclusão:** alertas chegando por email/Slack.
- **Risco/atenção:** Cloud Monitoring tem cota grátis ampla, mas dashboards e uptime checks fora da cota custam.

---

## Sumário rápido por fase

| Fase | Foco | Bloqueia? |
|---|---|---|
| 1 | Diagnóstico + ADRs | Não bloqueia código, mas alinha decisões |
| 2 | Setup do projeto Python e API | Pré-requisito para tudo |
| 3 | Endpoints HTTP | Frontend depende disso |
| 4 | Schema do DB | Pré-requisito para deploy cloud |
| 5 | Persistência SQL real | Pré-requisito para deploy cloud |
| 6 | Env + auth | Pré-requisito para produção |
| 7 | Frontend-readiness | Habilita time de frontend |
| 8 | Testes | Pré-requisito para CI |
| 9 | Docker | Pré-requisito para Cloud Run |
| 10 | CI | Habilita deploy automatizado |
| 11 | Deploy preparation | Pré-requisito para fase 12 |
| 12 | Deploy real | Final |

**Caminho crítico mais curto até "API em produção":** 2 → 3 → 4 → 5 → 6 → 9 → 10 → 11 → 12 (testes da fase 8 acoplados em paralelo desde a fase 3).
