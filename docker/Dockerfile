# syntax=docker/dockerfile:1
#
# Imagem de DESENVOLVIMENTO da API (e do worker Celery).
#
# Single-stage: inclui as ferramentas de compilação e as dependências de runtime.
# O código-fonte NÃO é tratado como imutável aqui — ele é montado em runtime via
# bind mount (ver docker-compose.yml), então alterações no host aparecem no
# container sem rebuild.
#
#   docker build -f Dockerfile -t praetor-api .
#   docker compose up --build

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# build-essential/libpq-dev: necessários para compilar dependências (ex.: psycopg).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala apenas as dependências a partir do pyproject (a app não é empacotada).
# Layer cacheável: só é invalidado quando o pyproject.toml muda.
COPY pyproject.toml ./
RUN pip install .

COPY . .

EXPOSE 8000

# Comando padrão; o compose de desenvolvimento o sobrescreve para incluir --reload.
CMD ["python", "manage.py", "run:server", "--host", "0.0.0.0", "--reload"]
