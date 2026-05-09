# ADR 0005 — Armazenamento do token de autenticação no frontend

**Status:** Aceito  
**Data:** 2026-05

---

## Contexto

A API emite um JWT no endpoint `POST /api/v1/auth/login`. O frontend (a ser implementado) precisa armazenar esse token e enviá-lo no header `Authorization: Bearer <token>` nas requisições subsequentes.

Há dois locais canônicos de armazenamento no browser:

| Local | Vulnerabilidade principal | Mitigação |
|---|---|---|
| `localStorage` / `sessionStorage` | XSS pode ler o token diretamente | Sanitização de output; CSP restritiva |
| Cookie `httpOnly` + `SameSite` | CSRF em mutações | CSRF token (double-submit cookie ou header custom) |

---

## Alternativas avaliadas

### Opção A — `localStorage`
- **Vantagem:** Simples de implementar; funciona bem em SPAs com chamadas cross-origin.
- **Desvantagem:** Qualquer script injetado via XSS tem acesso total ao token, que pode ser exfiltrado e reutilizado indefinidamente.
- **Risco:** Alto em aplicações com conteúdo gerado por usuário ou dependências de terceiros.

### Opção B — Cookie `httpOnly` + `SameSite=Lax` *(escolhida)*
- **Vantagem:** JavaScript nunca acessa o token (`httpOnly`); `SameSite=Lax` bloqueia CSRF em navegações cross-site de outros domínios.
- **Desvantagem:** Requer que o backend emita o cookie no login; chamadas cross-origin precisam de `credentials: 'include'` no fetch e `allow_credentials=True` + origens explícitas no CORS (proibido usar `*`).
- **Mitigação de CSRF:** Para mutações (`POST`, `PUT`, `DELETE`), exigir um header custom (ex: `X-Requested-With: XMLHttpRequest`) — browsers não enviam headers custom em requisições cross-site forjadas.

---

## Decisão

Usar **cookie `httpOnly` + `SameSite=Lax`** para o token de acesso.

O endpoint `POST /api/v1/auth/login` deve, além de retornar o `TokenOut` no body (compatibilidade), emitir um cookie:

```
Set-Cookie: access_token=<jwt>; HttpOnly; SameSite=Lax; Path=/api; Max-Age=3600
```

Em produção, adicionar `Secure` (HTTPS obrigatório).

---

## Consequências

- O backend precisará de um endpoint `POST /api/v1/auth/logout` que expire o cookie (`Max-Age=0`).
- O CORS deve listar origens explícitas; `allow_credentials=True` já está configurado.
- Em ambiente local (HTTP), o atributo `Secure` será omitido — controlado por `APP_ENV`.
- Clientes não-browser (Postman, curl, testes automatizados) continuam usando o Bearer token no header — o fluxo de cookie é aditivo, não substitutivo.
- Refresh token (rotação automática) fica para fase futura; por ora o JWT expira conforme `JWT_EXPIRES_MINUTES`.
