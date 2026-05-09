# Arquitetura Cliente-Servidor — Livraria

> **Status do documento:** versão inicial. Será iterada conforme o projeto evolui para HTTP/REST, banco gerenciado e deploy serverless no GCP.

---

## 1. Sumário executivo

Este documento descreve a **arquitetura cliente-servidor planejada** para o sistema da Livraria. Hoje o projeto é uma aplicação Python local (Tkinter + persistência em arquivos TXT) que segue **Clean Architecture**. O objetivo é evoluí-la para o modelo:

```
Cliente / Frontend (futuro)  →  Backend / API (HTTP/REST)  →  Banco de Dados (gerenciado)
```

mantendo a base de Clean Architecture já existente, **sem reescrever o domínio**, e preparando o caminho para deploy serverless de baixo custo no **Google Cloud Platform (GCP)**.

> **Observação importante:** o **frontend ainda NÃO foi desenvolvido**. O que existe hoje é uma interface gráfica Tkinter desktop (`livraria/views/tk_view.py`), que será substituída/complementada por um cliente web ou outro front consumindo a API REST. Nesta etapa **não** será criado frontend.

---

## 2. Sobre o PNG "Arquitetura Cliente-Servidor"

Foi solicitado o uso de um PNG chamado **"Arquitetura Cliente-Servidor"** (ou nome semelhante) como referência visual. **Não foi localizado nenhum arquivo de imagem (`.png`, `.jpg`, `.svg`, etc.) no repositório**.

Suposições adotadas (registradas para validação posterior):

- O PNG retrataria o triângulo clássico **Cliente → API → Banco**, possivelmente com uma camada de autenticação e/ou um diagrama paralelo para deploy em nuvem.
- Quando o PNG for adicionado ao repositório (sugestão: `docs/architecture/diagrams/cliente-servidor.png`), este documento deve ser revisado para garantir que o diagrama Mermaid abaixo reflete fielmente o desenho original.

**Pendência:** anexar o PNG em `docs/architecture/diagrams/` e atualizar este documento se houver divergência.

---

## 3. Estado atual do repositório

### 3.1. O que já existe

| Camada | Onde | Observações |
|---|---|---|
| **Domínio** | [livraria/domain/models/](../../livraria/domain/models/) | Entidades: `User`, `Book`, `Cart`/`CartItem`, `Order`/`OrderItem`, `Payment`, `Coupon`. Sem dependência de infra. |
| **Ports** | [livraria/domain/ports/](../../livraria/domain/ports/) | Interfaces ABC: `IUserRepository`, `IBookRepository`, `ICartRepository`, `IOrderRepository`, `IPaymentRepository`, `ICouponRepository`, `IUnitOfWork`. |
| **Use Cases** | [livraria/application/services/](../../livraria/application/services/) | `AuthService`, `BookService`, `CartService`, `CheckoutService`. Dependem só de ports. |
| **Controllers** | [livraria/controllers/](../../livraria/controllers/) | `AuthController`, `BookController`, `CartController`, `OrderController`. Hoje recebem chamadas direto da view Tkinter. |
| **Infra (persistência)** | [livraria/infrastructure/repositories_txt/](../../livraria/infrastructure/repositories_txt/) | Implementações concretas dos ports usando arquivos `.txt` (JSON Lines). `TxtUnitOfWork` provê atomicidade via snapshot em memória. |
| **Views** | [livraria/views/](../../livraria/views/) | `tk_view.py` (Tkinter) e `console_view.py`. Equivalem ao "cliente" atual da aplicação. |
| **Composition root** | [app.py](../../app.py), [example.py](../../example.py) | Monta o grafo de dependências. |
| **Dados (persistência local)** | [data/](../../data/) | `users.txt`, `books.txt`, `carts.txt`, `cart_items.txt`, `coupons.txt`, `orders.txt`, `order_items.txt`, `payments.txt`. |
| **Docs** | [README.md](../../README.md) | Visão geral do projeto, fluxos, estrutura. |

### 3.2. O que NÃO existe ainda

- ❌ **Camada HTTP / API REST** (não há FastAPI/Flask/Django/etc.).
- ❌ **Banco de dados real** (persistência hoje é arquivo TXT local).
- ❌ **Frontend web** (cliente atual é Tkinter desktop).
- ❌ **Autenticação baseada em token** (JWT/OAuth2). Auth atual é só comparação de hash em memória, sem sessão HTTP.
- ❌ **Variáveis de ambiente / arquivo `.env.example`**.
- ❌ **Testes automatizados** (não há diretório `tests/`).
- ❌ **Dockerfile / docker-compose**.
- ❌ **Pipeline CI/CD**.
- ❌ **Configuração de deploy GCP** (Cloud Run, Cloud SQL, Firestore, Artifact Registry, etc.).
- ❌ **Logging estruturado / observabilidade**.

---

## 4. Arquitetura cliente-servidor planejada

### 4.1. Visão geral

```
┌──────────────────┐    HTTP/HTTPS     ┌──────────────────────┐    SQL/NoSQL    ┌──────────────────┐
│  Cliente Web     │  ───────────────▶ │  Backend / API REST  │ ──────────────▶ │  Banco gerenciado│
│  (futuro)        │  ◀─────────────── │  (Python: FastAPI)   │ ◀────────────── │  (Cloud SQL /    │
│  React/Vue/etc.  │     JSON          │                      │                 │   Firestore)     │
└──────────────────┘                   └──────────────────────┘                 └──────────────────┘
                                                  │
                                                  │ valida JWT / sessão
                                                  ▼
                                        ┌──────────────────────┐
                                        │  Autenticação        │
                                        │  (futuro: JWT, OAuth2│
                                        │   ou Firebase Auth)  │
                                        └──────────────────────┘
```

### 4.2. Camadas

#### Cliente / Frontend (futuro)
- Aplicação web (sugestão: React/Vue/Next.js) ou cliente mobile.
- Não acessa banco diretamente. **Sempre passa pela API**.
- Comunicação via HTTP/REST + JSON. CORS configurado no backend.
- Autenticação: armazena token JWT (preferencialmente em cookie httpOnly) e o envia no header `Authorization: Bearer <token>`.
- Hospedagem futura sugerida: Firebase Hosting, Cloud Storage + Cloud CDN, ou Vercel/Netlify (todos têm tier gratuito).

#### Backend / API REST
- **Linguagem:** Python (mantendo a base atual).
- **Framework sugerido:** **FastAPI** (assíncrono, leve, bom para Cloud Run, gera OpenAPI automaticamente). Alternativa: Flask.
- Reutiliza **toda a camada de domínio + serviços + ports** já existente.
- Adiciona uma nova camada de **adapters HTTP** (em paralelo aos `controllers/` atuais), que traduz request HTTP → chamada de service → resposta JSON.
- Endpoints sugeridos (a detalhar em `steps-cliente-servidor.md`):
  - `POST /auth/register`, `POST /auth/login`
  - `GET /books`, `POST /books`, `GET /books/{id}`
  - `POST /carts`, `GET /carts/{id}`, `POST /carts/{id}/items`, `DELETE /carts/{id}/items/{book_id}`
  - `POST /orders/checkout`, `GET /orders/{id}`
  - `POST /orders/preview-discount`

#### Banco de dados
- **Hoje:** arquivos TXT (JSON Lines) em `data/`. Não escala, não suporta concorrência real, não roda em ambiente serverless stateless.
- **Futuro local/dev:** **SQLite** (zero setup) ou Postgres via Docker.
- **Futuro nuvem:** decidir entre:
  - **Cloud SQL (Postgres)** → relacional, familiar, integra fácil com SQLAlchemy. Custo: instância sempre ligada (a partir de ~US$ 9/mês na menor). **Não é serverless puro**, mas tem tier mais barato.
  - **Firestore (modo Native)** → NoSQL serverless, **paga por uso**, free tier generoso. Exige repensar o modelo (sem JOINs).
  - **AlloyDB Omni / Cloud SQL com auto-pause** → opções intermediárias para reduzir custo.
- **Recomendação inicial:** começar com **Cloud SQL Postgres na menor instância** (mais próximo do modelo atual e do conhecimento típico do time) e avaliar Firestore caso o custo precise cair mais.

#### Camada de autenticação
- Hoje: comparação de hash MD5/SHA local — **inadequado para produção**.
- Futuro próximo: hash com `bcrypt`/`argon2` + emissão de **JWT** assinado.
- Futuro alternativo (mais barato/ágil): **Firebase Authentication** (free tier robusto, integra com GCP, não precisa gerenciar tabela de usuários).

### 4.3. Comunicação HTTP/REST

- Protocolo: **HTTPS** obrigatório em produção (Cloud Run já provê certificado gerenciado).
- Formato: **JSON**. Pydantic (FastAPI) cuida de validação e serialização.
- Versionamento sugerido: prefixo `/api/v1/...`.
- Erros padronizados: `{"error": "...", "code": "...", "details": {...}}` com status HTTP coerente.
- **CORS:** liberar apenas origens conhecidas (lista de domínios do frontend) via env var.

### 4.4. Variáveis de ambiente

Lista mínima esperada (a ser materializada em `.env.example`):

```
APP_ENV=local|staging|production
APP_PORT=8080
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/livraria
# ou para SQLite local:
# DATABASE_URL=sqlite:///./data/livraria.db
JWT_SECRET=change-me
JWT_EXPIRES_MINUTES=60
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.exemplo.com
LOG_LEVEL=INFO
```

**Nunca** commitar `.env` real. Em GCP, valores sensíveis devem vir do **Secret Manager**, montados como variáveis de ambiente em deploy.

---

## 5. Diagrama (Mermaid) — atual e futuro

```mermaid
flowchart LR
    %% ===== Estado atual =====
    subgraph Atual["Estado atual (local, sem rede)"]
        TkUser["Usuário (desktop)"] --> TkView["Tkinter / Console (views/)"]
        TkView --> Ctrl["Controllers"]
        Ctrl --> Svc["Application Services"]
        Svc --> Ports["Domain Ports (ABC)"]
        Ports -.implementadas por.-> TxtRepo["TxtRepositories"]
        TxtRepo --> Files[("data/*.txt — JSON Lines")]
    end

    %% ===== Estado futuro =====
    subgraph Futuro["Estado futuro (cliente-servidor)"]
        WebUser["Usuário (browser/mobile)"] --> Frontend["Frontend futuro<br/>(React/Vue/etc.)"]
        Frontend -- HTTPS / JSON --> API["Backend / API REST<br/>(FastAPI - Python)"]
        API --> Auth["Camada de Auth<br/>(JWT ou Firebase Auth)"]
        API --> Svc2["Application Services<br/>(reaproveitados)"]
        Svc2 --> Ports2["Domain Ports"]
        Ports2 -.implementadas por.-> SqlRepo["SqlAlchemyRepositories<br/>(novos)"]
        SqlRepo --> ManagedDB[("Banco gerenciado<br/>Cloud SQL / Firestore")]
    end

    %% ===== Pipeline cloud =====
    subgraph Cloud["Cloud / CI-CD futuro (GCP)"]
        Repo["GitHub Repository"] --> CI["CI/CD<br/>(GitHub Actions ou Cloud Build)"]
        CI --> AR["Artifact Registry<br/>(imagens Docker)"]
        AR --> CR["Cloud Run<br/>(serverless, paga por uso)"]
        CR --> ManagedDB
        Secrets["Secret Manager"] --> CR
    end

    API -. mesmo runtime, deploy em .-> CR
    Frontend -. hospedado em .-> Hosting["Firebase Hosting / Cloud Storage + CDN"]
```

---

## 6. Como o backend deve se comunicar com o banco

**Princípio:** manter a **Dependency Rule** já adotada. O domínio e os serviços continuam dependendo apenas dos `ports` (`IBookRepository`, etc.). O que muda é **quem implementa esses ports**.

Plano de evolução:

1. Criar um novo pacote `livraria/infrastructure/repositories_sql/` (ou `repositories_db/`).
2. Implementar cada port usando **SQLAlchemy 2.x** (Core ou ORM) e Alembic para migrations.
3. Manter `repositories_txt/` em paralelo durante a transição (útil para testes locais sem Docker).
4. O **composition root** (`app.py` para a CLI/Tk; e o novo `main.py`/`api/main.py` para a API HTTP) escolhe qual implementação injetar via env var (`PERSISTENCE=txt|sql`).
5. `IUnitOfWork` passa a ser implementada como `SqlUnitOfWork` (transação real de DB), substituindo o snapshot em memória.

Resultado: nenhum service ou model precisa ser tocado.

---

## 7. Como o frontend futuro consumirá a API

- O frontend será um cliente **stateless do ponto de vista do servidor** — toda a sessão vive num token (JWT) no cliente.
- Fluxo típico (exemplo de checkout):
  1. `POST /api/v1/auth/login` → recebe JWT.
  2. `GET /api/v1/books` → lista catálogo.
  3. `POST /api/v1/carts/{id}/items` → adiciona itens.
  4. `POST /api/v1/orders/preview-discount` → preview de cupom.
  5. `POST /api/v1/orders/checkout` → finaliza.
- Documentação automática: FastAPI expõe **OpenAPI / Swagger UI** em `/docs`, que serve como contrato vivo entre frontend e backend.
- Erros e validações vêm padronizados (Pydantic + handlers globais), simplificando o trabalho do cliente.

---

## 8. Evolução para GCP serverless de baixo custo

### 8.1. Princípios
- **Serverless first:** preferir serviços que escalam a zero e cobram por uso.
- **Sem servidores ociosos:** evitar Compute Engine 24/7 e instâncias mínimas pagas full-time onde possível.
- **Free tier máximo:** Cloud Run, Cloud Functions, Firestore, Cloud Storage e Firebase Hosting têm cotas gratuitas mensais relevantes.
- **Imagens leves:** Dockerfiles slim/distroless reduzem cold start e custo de storage no Artifact Registry.

### 8.2. Stack-alvo recomendado

| Componente | Serviço GCP | Justificativa |
|---|---|---|
| API HTTP | **Cloud Run** | Serverless, escala a zero, paga por requisição+CPU+memória. Aceita qualquer container. |
| Banco relacional | **Cloud SQL Postgres (db-f1-micro)** | Mais barato que outras opções relacionais; pode ser parado fora do horário em dev. |
| Banco alternativo | **Firestore (Native)** | NoSQL totalmente serverless, free tier generoso. Avaliar se o modelo se adapta. |
| Imagens Docker | **Artifact Registry** | Registry oficial do GCP, integra com Cloud Build/Cloud Run. |
| Build/CI | **Cloud Build** ou **GitHub Actions** | Cloud Build tem free tier (120 min/dia). GitHub Actions é simples para começar. |
| Secrets | **Secret Manager** | Não commitar `.env`. Montar secrets em variáveis de ambiente do Cloud Run. |
| Auth | **Firebase Authentication** (opcional) | Elimina necessidade de manter tabela de usuários e fluxo de senha. |
| Frontend hosting | **Firebase Hosting** ou **Cloud Storage + Cloud CDN** | Free tier amplo, certificado HTTPS automático. |
| Logs/observabilidade | **Cloud Logging** (já incluso no Cloud Run) | Sem custo adicional para volume baixo. |

### 8.3. Estratégia de baixo custo
- Cloud Run com **min-instances = 0** (aceita cold start em troca de custo zero quando ocioso).
- **Concurrency** alta (até 80 reqs/instância) para minimizar nº de instâncias.
- Cloud SQL: usar a menor instância (`db-f1-micro`) e **parar a instância em dev** quando não estiver em uso.
- Alternativa para zerar custo de DB em dev: **SQLite local** ou **Firestore** (paga só pelas leituras/escritas reais).
- Configurar **alertas de orçamento** em GCP Billing.
- Não habilitar VPC connector, Cloud NAT, Cloud Load Balancer, etc. enquanto não houver necessidade real (custo fixo).
- Política de **logs/retention curto** em dev.

### 8.4. CI/CD futuro
- Branch `main` → deploy automático em **staging** (Cloud Run service `livraria-api-staging`).
- Tag `v*.*.*` → deploy em **produção** (Cloud Run service `livraria-api-prod`).
- Pipeline: `lint → test → build (docker) → push (Artifact Registry) → deploy (Cloud Run)`.
- Migrations de banco rodam como **job separado** antes do deploy da API (Cloud Run Jobs ou step do pipeline).

---

## 9. Pendências, riscos e recomendações

### 9.1. Pendências técnicas
- [ ] Anexar PNG "Arquitetura Cliente-Servidor" em `docs/architecture/diagrams/`.
- [ ] Escolher framework HTTP (recomendado: FastAPI).
- [ ] Escolher banco de dados-alvo (recomendado: Cloud SQL Postgres; alternativa: Firestore).
- [ ] Definir estratégia de autenticação (JWT próprio vs Firebase Auth).
- [ ] Criar `.env.example` e adotar `pydantic-settings` ou `python-decouple`.
- [ ] Criar diretório `tests/` com testes unitários (services) e de integração (API).
- [ ] Criar `Dockerfile` (slim, multi-stage) e `docker-compose.yml` para dev local com Postgres.
- [ ] Definir contrato OpenAPI dos endpoints.
- [ ] Definir política de versionamento da API (`/api/v1`).

### 9.2. Riscos
- **Persistência atual em TXT não sobrevive a ambiente serverless** (filesystem efêmero do Cloud Run + sem concorrência). A migração para banco gerenciado é **bloqueante** para deploy cloud.
- **Auth atual é insegura** (hash sem salt, sem token, sem expiração). Não pode ir para produção como está.
- **Custo no GCP pode escapar** se: instâncias mínimas > 0, Cloud SQL não for parada em dev, Cloud Build sem cap de minutos, etc.
- **Cold start no Cloud Run** pode impactar UX. Mitigação futura: `min-instances=1` apenas em produção, se necessário (com custo).
- **Vendor lock-in:** Firestore amarra mais que Postgres. Avaliar antes de adotar.

### 9.3. Recomendações
- Manter **`repositories_txt/` como modo "demo"/fallback** — útil em testes e em apresentações sem dependências.
- Adotar **`pre-commit`** com `ruff` + `black` + `mypy` para garantir qualidade antes de CI.
- Quando criar a API, **expor um endpoint `/health`** desde o início (necessário para health checks do Cloud Run).
- Documentar todas as decisões arquiteturais em **ADRs** simples em `docs/adr/`.
- Não criar nenhum recurso pago no GCP antes do projeto estar pronto para deploy.

---

## 10. Inconsistências entre o cenário pedido e o estado atual

| Item pedido | Estado real | Resolução |
|---|---|---|
| PNG "Arquitetura Cliente-Servidor" | Não está no repo | Documentado como pendência (seção 2). |
| "Frontend ainda não desenvolvido" | Existe Tkinter desktop, mas nenhum frontend web/HTTP | Documentado: Tkinter é o "cliente atual local"; o **frontend HTTP é que ainda não existe**. |
| "API/backend" | Não há camada HTTP. Há apenas serviços Python chamados in-process pela GUI | Mapeado: criar camada HTTP por cima dos services existentes (seção 4 + steps). |
| "Banco de dados" | TXT JSON Lines | Migração planejada para banco gerenciado (seção 6 + steps). |
| "Variáveis de ambiente" | Nenhuma — caminhos hard-coded | Será criado `.env.example` e config via pydantic-settings (steps fase 6). |
| "Docker" | Inexistente | Steps fase 9. |
| "CI/CD" | Inexistente | Steps fase 10. |

Ver passos detalhados em [steps-cliente-servidor.md](steps-cliente-servidor.md).
