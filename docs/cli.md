# CLI & Code Generation

`backend/manage.py` is the primary tool for managing the lifecycle of your application. Rode-o a partir de `backend/` (`cd backend`) ou, da raiz do repositório, como `python backend/manage.py <comando>` — nenhum caminho depende do diretório de trabalho.

Os comandos estão divididos em dois grupos:

- **Runtime (ops)** — `backend/core/commands/`. Fazem parte da imagem de produção (`run:server`, `run:worker`, `db:*`, `auth:*`, `shell`).
- **Geradores (dev-only)** — `tools/commands/`, com os templates Jinja2 em `tools/templates/` e os caminhos centralizados em `tools/paths.py`. **Não** entram na imagem de produção (o contexto de build do backend é `backend/`), então `make:*`, `rm:*` e `generate:*` só existem rodando a partir do repositório.

## General Commands

- `python manage.py run:server`: Starts the Uvicorn dev server.
- `python manage.py shell`: Starts an interactive Python shell with the app context.
- `python manage.py run:test [app]`: Runs the test suite with `pytest`.

## Database Management

- `python manage.py db:makemigrations -m "message"`: Create a new migration.
- `python manage.py db:migrate`: Upgrade database to the latest version.
- `python manage.py db:rollback`: Downgrade database one step.

> **Caminho canônico:** use `db:migrate` (migrações versionadas em `backend/migrations/versions/`)
> para subir o schema. `db:create` cria as tabelas diretamente a partir dos models e
> serve para desenvolvimento rápido, dispensando o histórico de migrações.

## Code Generation (`make`)

The `make` commands ensure architectural consistency by generating boilerplate for both backend and frontend.

### Creating an App
```bash
python manage.py make:app <app_name>
```
Created the modular app structure in `backend/apps/` and a corresponding domain folder in `frontend/src/features/`.

### Creating an Entity
```bash
python manage.py make:entity <entity_name> --app <app_name>
```
Generates a complete vertical slice of the feature:
- **Backend** (em `backend/apps/<app>/`):
    - `models/{entity}.py`, `schemas/{entity}.py`
    - `repositories/{entity}.py`, `services/{entity}.py`
    - `routers/{entity}.py`, `permissions/{entity}.py`, `tests/test_{entity}.py`
- **Frontend** (em `frontend/src/features/`):
    - `frontend/src/features/{app}/{entity}/service.ts` (API Client)
    - `frontend/src/features/{app}/{entity}/pages/List.tsx` (**DataTable** view)
    - `frontend/src/features/{app}/{entity}/routes.tsx` (Auto-discovered routes)
    - `frontend/src/features/{app}/{entity}/schema.ts` (Zod validations)
    - `frontend/src/features/{app}/{entity}/types.ts` (TS interfaces)

Use `--no-frontend` to skip frontend code generation.

## Code Removal (`rm`)

- `python manage.py rm:app <app_name>`: Deletes the app and cleans up frontend feature directories.
- `python manage.py rm:entity <entity_name> --app <app_name>`: Deletes the entity and its specific frontend module.
