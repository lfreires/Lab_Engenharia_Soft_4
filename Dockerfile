# ── Stage 1: build wheels ──────────────────────────────────────────────────
# Compilar todas as dependências em wheels para que o stage final
# não precise de compiladores nem acesso à internet.
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip --quiet && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ── Stage 2: imagem de runtime ─────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Usuário não-root (boas práticas de segurança para Cloud Run)
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser

# Instalar deps a partir dos wheels pré-compilados (sem internet)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl && \
    rm -rf /wheels

# Copiar código da aplicação
COPY livraria/ ./livraria/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Python encontra o pacote 'livraria' em /app
ENV PYTHONPATH=/app

# Cloud Run injeta $PORT (padrão 8080)
ENV PORT=8080
EXPOSE 8080

USER appuser

CMD ["sh", "-c", "uvicorn livraria.api.main:app --host 0.0.0.0 --port ${PORT}"]
