# ADR 0001 — Framework HTTP

**Status:** Aceito  
**Data:** 2026-05-09  
**Autores:** Lucas Freires

---

## Contexto

O projeto atual é uma aplicação Python local com GUI Tkinter. Para evoluir para arquitetura cliente-servidor, precisamos de um framework HTTP que:

- Exponha os services existentes como API REST/JSON.
- Gere documentação OpenAPI automaticamente (necessário para o frontend futuro consumir um contrato vivo).
- Seja leve o suficiente para rodar em **Cloud Run com `min-instances=0`** (cold start importa).
- Se encaixe bem com **Clean Architecture** — injeção de dependências via código, não magia de framework.
- Use as type annotations já presentes em todo o codebase (`dataclasses`, `from __future__ import annotations`).

**Candidatos avaliados:**

| Critério | FastAPI | Flask |
|---|---|---|
| OpenAPI / Swagger automático | Sim (nativo) | Não (requer extensão `flask-restx` ou similar) |
| Validação de entrada | Pydantic v2 nativo | Manual ou extensão |
| Type hints de rota | Sim (parâmetros tipados viram validação) | Não |
| Injeção de dependências | `Depends()` — funciona bem com Clean Arch | Não tem; usa `g`, `current_app`, ou factories manuais |
| Desempenho / tamanho | Leve (~5 MB instalado, ASGI async) | Leve (~2 MB, WSGI sync) |
| Maturidade | Alta (v0.115+, amplamente usado) | Alta (v3+, projeto maduro) |
| Cold start em Cloud Run | Bom | Bom |
| Curva de aprendizado | Baixa para quem conhece Python moderno | Muito baixa, mas requer mais boilerplate |

---

## Decisão

**Adotar FastAPI.**

### Justificativas

1. **OpenAPI nativo sem extensão** — o endpoint `/docs` (Swagger UI) e `/openapi.json` ficam disponíveis desde o primeiro `uvicorn ... app`. Isso entrega imediatamente o contrato para o time de frontend.
2. **Pydantic v2 integrado** — validação e serialização de DTOs de entrada/saída sem código extra. Evita vazar entidades de domínio na resposta.
3. **`Depends()` mapeia diretamente para injeção de dependências** — cada router declara explicitamente quais services precisa; o composition root vive em `deps.py`, preservando a Dependency Rule do Clean Architecture.
4. **ASGI + uvicorn** — suporte nativo a async se necessário no futuro (e.g., acesso async ao banco via `asyncpg`). Flask exigiria migração para Quart ou outro adapter ASGI.
5. **Type hints aproveitados** — o codebase já usa tipos rigorosos. FastAPI lê esses tipos para gerar validação e documentação automaticamente, sem duplicação.

### O que não muda

- Nenhuma camada de domínio, service ou port é alterada.
- Os controllers Tkinter existentes continuam funcionando.
- `app.py` (Tkinter) e o novo `livraria/api/main.py` (HTTP) coexistem; ambos são composition roots independentes que injetam as mesmas implementações concretas.

---

## Consequências

**Positivas:**
- Documentação da API gerada automaticamente e sempre atualizada.
- Menos código boilerplate nos routers.
- Facilita adição de validação de request sem modificar services.

**Negativas / atenções:**
- Pydantic v2 tem algumas diferenças de migração em relação à v1. Usar `model_config = ConfigDict(from_attributes=True)` para converter entidades de domínio para schemas.
- FastAPI usa ASGI; se alguma biblioteca de banco for síncrona, usar `run_in_executor` ou `asyncio` adequadamente para não bloquear o event loop.
- Versão a travar: `fastapi>=0.115,<1.0` (ainda pré-1.0).

---

## Dependências a adicionar

```
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30
pydantic>=2.7
pydantic-settings>=2.3
```
