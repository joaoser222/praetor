# Getting Started

Get your Praetor project up and running in minutes.

> **Onde rodar os comandos:** a CLI do backend vive em `backend/manage.py`, então os
> comandos abaixo partem de `backend/` (`cd backend`). Da raiz do repositório, o
> equivalente é `python backend/manage.py <comando>` — nenhum caminho depende do CWD.

## 1. Environment Setup

```bash
# Clone and enter the project
git clone <repo_url>
cd praetor

# Setup Python environment (a partir de backend/)
python -m venv venv
source venv/bin/activate
cd backend
pip install -e ".[dev]"
cd ..

# Initial configuration (na raiz, compartilhada com o Docker Compose)
cp .env.example .env
```

## 2. Initialize Database & Security

```bash
cd backend

# Apply migrations (o projeto já inclui a migração inicial do schema)
python manage.py db:migrate

# Create an Admin user
python manage.py auth:createsuperuser

# Generate initial system permissions
python manage.py auth:makepermissions
```

> Para desenvolvimento rápido, `python manage.py db:create` cria as tabelas
> diretamente a partir dos models, sem usar o histórico de migrações.

## 3. The Development Loop

### Step 1: Generate a Feature
```bash
cd backend

# Create an app (domain)
python manage.py make:app store

# Create an entity (module)
python manage.py make:entity product --app store
```

Os geradores (`make:*`, `rm:*`, `generate:*`) vivem em `tools/` e **não** fazem
parte da imagem de produção: eles só existem quando a pasta `tools/` está presente
(comando rodando do repositório, não de dentro da imagem do backend).

### Step 2: Run the APIs
```bash
cd backend
python manage.py run:server
```

## 4. Frontend Integration

Praetor comes with a professional **React + Vite + Mantine** frontend.

```bash
cd frontend
npm install
npm run dev
```

### Fullstack Power
When you run `make:entity`, the system automatically generates:
1.  **Backend logic**: models, routers, and services.
2.  **Frontend views**: A complete **DataTable** with CRUD actions.
3.  **Automatic Routing**: The new page is instantly visible in the Sidebar menu.

## 5. Deployment with Docker

The container setup lives in `docker/`: the shared components
(`docker/compose/base.yml`) are imported by two environments via Compose's
`include` (`docker/compose/develop.yml` and `docker/compose/production.yml`).
Both read the same central `.env`.

**Development** (SQLite + Vite dev server):

```bash
cp .env.example .env
docker compose up --build
```

**Production** (PostgreSQL + nginx) — set `SECRET_KEY` and `POSTGRES_PASSWORD` in `.env` first:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```
