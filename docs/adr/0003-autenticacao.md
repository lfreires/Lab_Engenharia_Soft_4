# ADR 0003 — Estratégia de autenticação

**Status:** Aceito  
**Data:** 2026-05-09  
**Autores:** Lucas Freires

---

## Contexto

O sistema atual tem autenticação de usuário via comparação de hash. Problemas identificados:

1. **Hash inseguro:** `sha256(password.encode("utf-8")).hexdigest()` — SHA-256 puro, **sem salt**. Vulnerável a rainbow tables e ataques de dicionário.
2. **Sem sessão HTTP:** a autenticação valida credenciais in-process e retorna `bool`. Não há token, cookie ou mecanismo de sessão.
3. **Sem autorização:** não há roles (admin vs. usuário comum), nem controle de quem pode criar livros, por exemplo.

Para a API REST, precisamos de um mecanismo que:

- Autentique requests HTTP sem estado (stateless).
- Proteja rotas que exigem login.
- Seja seguro o suficiente para produção.
- Seja simples de implementar sem criar dependências desnecessárias.

**Candidatos avaliados:**

| Critério | JWT próprio (PyJWT) | Firebase Authentication |
|---|---|---|
| Complexidade de implementação | Baixa (emitir + validar token) | Muito baixa (SDK faz tudo) |
| Dependências externas | Apenas `pyjwt` | SDK Firebase + projeto Firebase |
| Controle sobre tokens | Total | Limitado (Firebase emite os tokens) |
| Social login (Google, GitHub…) | Não | Sim (nativo) |
| Email verification / reset senha | Manual | Sim (nativo) |
| Custo | Grátis | Free tier generoso (10k auth/mês grátis) |
| Curva de aprendizado | Baixa | Baixa (SDK bem documentado) |
| Vendor lock-in | Nenhum | Google / Firebase |
| Hash de senha | Responsabilidade nossa | Firebase gerencia |
| Adequação ao projeto atual | Alta | Requer integrar SDK + repensar User model |

---

## Decisão

**Adotar JWT próprio com PyJWT** nesta fase, com hash de senha em **bcrypt**.

### Justificativas

1. **Controle total e zero vendor lock-in** — o sistema usa `IUserRepository` para persistência de usuários. Firebase Auth exigiria que a identidade fosse gerenciada externamente, complicando a integração com o `User` domain model atual.

2. **Simplicidade agora** — para o escopo atual (login/registro com usuário+senha, sem social login, sem verificação de email), JWT próprio é suficiente e mais didático.

3. **Bcrypt como substituto imediato** — a única mudança no domínio é trocar `sha256(...)` por `bcrypt.hashpw(...)` em `User.hash_password`. O resto dos services e repositórios não muda.

4. **Firebase Auth pode ser adotado no futuro** — se o projeto evoluir para social login ou precisar de email verification, Firebase Auth pode substituir o JWT próprio com mudança relativamente localizada (um novo `FirebaseAuthService` implementando os ports de auth).

### Fluxo de autenticação planejado

```
POST /api/v1/auth/login
  └─ AuthService.authenticate(username, password)
      └─ IUserRepository.find(username) → (username, password_hash)
      └─ bcrypt.checkpw(password, password_hash) → bool
  └─ JwtService.create_token(username) → str (JWT assinado)
  └─ Resposta: { "access_token": "...", "token_type": "bearer" }

Rotas protegidas:
  Authorization: Bearer <token>
  └─ deps.get_current_user()
      └─ JwtService.decode_token(token) → username
      └─ IUserRepository.exists(username) → valida que ainda existe
  └─ username injetado no handler
```

### Claims do JWT

```json
{
  "sub": "admin",
  "exp": 1716300000,
  "iat": 1716296400,
  "type": "access"
}
```

Sem roles por enquanto — adicionar `"role": "admin"|"user"` quando a funcionalidade de autorização for necessária.

---

## Mudanças necessárias no domínio

**Arquivo:** `livraria/domain/models/user.py`

```python
# Antes (inseguro):
@staticmethod
def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()

# Depois (seguro):
@staticmethod
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

@staticmethod
def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
```

> **Atenção de migração:** usuários cadastrados antes da troca terão hash SHA-256. Na primeira autenticação após a migração, o check por bcrypt falhará. Estratégia recomendada: na etapa de migração do banco (Alembic), marcar todos os usuários como `password_needs_reset = True` e exigir redefinição de senha no primeiro login pós-migração.

---

## Consequências

**Positivas:**
- Autenticação segura sem dependências pesadas.
- JWT stateless — Cloud Run pode escalar horizontalmente sem sessão compartilhada.
- `JWT_SECRET` vem do Secret Manager em produção (nunca commitado).

**Negativas / atenções:**
- JWT sem revogação nativa — logout invalida o token apenas no cliente. Se precisar de revogação (e.g., "deslogar todos os dispositivos"), será necessário uma blocklist em Redis ou similar no futuro.
- Responsabilidade pelo hash de senha é nossa — bcrypt está bem estabelecido, mas precisa ser mantido (custo de work factor com hardware mais rápido).
- **Não implementar** refresh tokens nesta fase — expiração curta (60 min) + re-login é suficiente para o MVP.

---

## Dependências a adicionar

```
bcrypt>=4.2
pyjwt>=2.9
```
