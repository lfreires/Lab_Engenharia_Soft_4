# Banco Gerenciado no GCP - Step 11.3 (Opcao B Firestore)

Este documento define como usar Cloud Firestore (Native mode) como persistencia da API.

## Objetivo

- Usar banco serverless com custo por uso.
- Evitar custo fixo de banco 24/7 em ambiente ocioso.
- Manter os services intactos e trocar apenas infraestrutura.

## Decisao

- Backend de persistencia no deploy: `PERSISTENCE_BACKEND=firestore`.
- SDK: `google-cloud-firestore`.
- Repositorios: `livraria/infrastructure/repositories_firestore/`.

## 1. Habilitar Firestore (Native mode)

No console:

1. Firestore Database -> Create database.
2. Modo: Native.
3. Regiao sugerida: `us-central1` (mesma do Cloud Run).
4. Rules iniciais: production mode.

## 2. Colecoes usadas pela API

- `users`
- `books`
- `carts/{cartId}/items`
- `orders/{orderId}/items`
- `payments`
- `coupons`

## 3. IAM minimo para runtime

Service account do Cloud Run (`livraria-api-runtime`) precisa:

- `roles/datastore.user` (leitura/escrita no Firestore)
- `roles/secretmanager.secretAccessor` (JWT secret)
- `roles/logging.logWriter`

## 4. Variaveis de ambiente no Cloud Run

```text
APP_ENV=staging|production
PERSISTENCE_BACKEND=firestore
FIRESTORE_PROJECT_ID=<project-id>
FIRESTORE_DATABASE=(default)
```

Secret:

- `JWT_SECRET` via Secret Manager (`livraria-jwt-secret:latest`)

## 5. Validacao pos-deploy

1. Fazer login em `/api/v1/auth/login` (seed local em dev, usuario real em staging/prod).
2. Criar carrinho e checkout.
3. Verificar no Firestore:
   - novo documento em `orders`
   - itens em `orders/{id}/items`
   - pagamento em `payments/{id}`
   - estoque atualizado em `books`

## Tradeoffs

- Pro: escala a zero no backend + banco com cobranca por uso.
- Contra: sem joins SQL e modelagem mais orientada a documentos.
- Contra: transacoes e queries complexas exigem mais cuidado de modelagem.
