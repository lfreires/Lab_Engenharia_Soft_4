# IAM e Service Accounts - GCP

Permissoes minimas para CI/CD e runtime da API no Cloud Run.

## Principio

- Menor privilegio.
- Nao usar `roles/owner` nem `roles/editor`.
- Opcao B (Firestore) como padrao desta fase.

## 1. Service account de runtime

Nome: `livraria-api-runtime`

Roles:

- `roles/datastore.user` (Firestore Native mode)
- `roles/secretmanager.secretAccessor` (secrets usados pela API)
- `roles/logging.logWriter`

Comandos:

```bash
gcloud iam service-accounts create livraria-api-runtime \
  --display-name="Livraria API runtime" \
  --project="$PROJECT_ID"

for role in roles/datastore.user roles/secretmanager.secretAccessor roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:livraria-api-runtime@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="$role"
done
```

Escopo recomendado para secret:

```bash
gcloud secrets add-iam-policy-binding livraria-jwt-secret \
  --member="serviceAccount:livraria-api-runtime@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 2. Service account de CI/CD

Nome: `livraria-ci-deployer`

Roles:

- `roles/artifactregistry.writer`
- `roles/run.admin`
- `roles/iam.serviceAccountUser`

Comandos:

```bash
gcloud iam service-accounts create livraria-ci-deployer \
  --display-name="Livraria CI deployer" \
  --project="$PROJECT_ID"

for role in roles/artifactregistry.writer roles/run.admin roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:livraria-ci-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="$role"
done
```

## 3. Workload Identity Federation (GitHub Actions)

```bash
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions pool" \
  --project="$PROJECT_ID"

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='<ORG>/<REPO>'" \
  --project="$PROJECT_ID"

gcloud iam service-accounts add-iam-policy-binding \
  "livraria-ci-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/<ORG>/<REPO>"
```

Secrets no GitHub:

- `WIF_PROVIDER`
- `WIF_SERVICE_ACCOUNT`

Variable no GitHub:

- `GCP_PROJECT_ID`

## 4. Observacao para opcao A (Cloud SQL)

Se em algum momento voltar para Cloud SQL, acrescentar `roles/cloudsql.client` na runtime SA.
