# Livraria - Arquitetura Cliente-Servidor

## 1) Visao geral

Este projeto implementa um sistema de livraria em arquitetura cliente-servidor, com:

- frontend web para uso do sistema
- backend REST para regras de negocio
- autenticacao com JWT
- persistencia em Firestore (opcao B)
- deploy em nuvem com pipeline CI/CD

## 2) Arquitetura do projeto

- Frontend: React + Vite (`frontend/`)
- Backend: FastAPI (`livraria/api`)
- Camadas (Clean Architecture):
  - `domain`: entidades e contratos
  - `application/services`: casos de uso
  - `infrastructure`: repositorios SQL/Firestore
  - `api`: rotas, schemas e autenticacao

## 3) Funcionalidades implementadas

- cadastro e login de usuario
- listagem e cadastro de livros
- criacao e gerenciamento de carrinho
- aplicacao de cupom (preview de desconto)
- checkout com baixa de estoque

## 4) Links de deploy

- Frontend (Vercel): [https://lab-engenharia-soft-4.vercel.app](https://lab-engenharia-soft-4.vercel.app)
- Backend staging (Cloud Run): [https://livraria-api-staging-jar2vmuxea-uc.a.run.app](https://livraria-api-staging-jar2vmuxea-uc.a.run.app)
- Swagger da API: [https://livraria-api-staging-jar2vmuxea-uc.a.run.app/docs](https://livraria-api-staging-jar2vmuxea-uc.a.run.app/docs)

## 5) Como executar localmente

### Backend

```bash
pip install -e ".[dev]"
cp .env.example .env
uvicorn livraria.api.main:app --reload
```

API local:
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Obs.: configurar `VITE_API_BASE_URL` para o backend desejado (local ou staging).

## 6) Como validar rapidamente (smoke test)

1. Registrar usuario
2. Fazer login
3. Listar livros
4. Adicionar livro ao carrinho
5. Aplicar cupom (opcional)
6. Finalizar pedido
7. Confirmar reducao de estoque
8. Confirmar carrinho limpo apos checkout

## 7) Qualidade e CI/CD

- CI com GitHub Actions:
  - lint (`ruff check`, `ruff format --check`)
  - testes com cobertura
- Deploy automatico:
  - push em `main` -> staging no Cloud Run
  - tags `v*.*.*` -> producao

## 8) Documentacao complementar

- `docs/architecture/cliente-servidor.md`
- `docs/architecture/steps-cliente-servidor.md`
- `docs/architecture/gcp-setup.md`
