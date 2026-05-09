# GCP Setup - Step 11.1

Guia de preparacao do projeto no Google Cloud antes de criar recursos pagos.

## Objetivo

- Criar o projeto GCP do backend.
- Ativar APIs obrigatorias.
- Configurar alertas de billing em US$ 5, US$ 10 e US$ 20.
- Confirmar que ainda nao existe recurso pago ativo.

## 1. Variaveis base

```bash
export PROJECT_ID="livraria-<sufixo-unico>"
export PROJECT_NAME="Livraria API"
export BILLING_ACCOUNT="<billing-account-id>"
```

## 2. Criar projeto e vincular billing

```bash
gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME"

gcloud beta billing projects link "$PROJECT_ID" \
  --billing-account="$BILLING_ACCOUNT"
```

## 3. Ativar APIs necessarias

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  --project "$PROJECT_ID"
```

## 4. Criar alertas de budget

No console:

1. Billing -> Budgets & alerts -> Create budget.
2. Scope: projeto `"$PROJECT_ID"`.
3. Amount: US$ 20 (mensal).
4. Threshold rules: 25%, 50%, 100% (equivale a US$ 5, 10, 20).
5. Notification channel: email do time.

Opcional: criar 3 budgets separados (5, 10, 20) se preferirem alertas independentes.

## 5. Checklist de conclusao

- Projeto criado e associado ao billing.
- APIs ativadas com sucesso.
- Alertas ativos.
- Cloud Run / Firestore / Artifact Registry sem instancias ou servicos criados manualmente.

## Riscos e atencoes

- Ativar API nao gera custo direto, mas criar recursos gera.
- Sempre validar o dashboard de billing apos cada passo.
- Nao criar `min-instances > 0` no Cloud Run em staging sem necessidade.
