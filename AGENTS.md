# AGENTS.md

Full-stack boilerplate: **FastAPI** backend (modular apps, repository/service layers) in `backend/`, **React 19 + Vite + TypeScript** frontend in `frontend/`, and dev-only generators in `tools/`, all orchestrated by the Click CLI `manage.py`. See `docs/` for the narrative documentation; this file records what is not obvious from it.

## Project skills (`.agents/skills/`)
Agent procedures live in skills, written in **English**. Triggers are exact words typed by the user; any other wording does not activate a skill.

| Trigger | Skill | Use |
|---|---|---|
| `commit` | `git-commit` | Groups changes into Angular-style commits with pt-BR descriptions; commits and pushes only after confirmation |
| `publish` | `publish-workflow` | PR from a `feature/*` or `bugfix/*` branch into `develop` |
| `publish_production` | `publish-workflow` | Release: PR `develop` → `master`, tag `vX.Y.Z`, syncs `develop` |
| `planner` / `apply` | `planning-and-task-breakdown` | Plans a feature under `workspace/changes/`; executes only with no open questions |
| code generation request | `project-codegen` | `make:*`, `rm:*`, `generate:schemas` |
| migration request | `database-migrations` | `db:*` and the canonical order (`db:migrate`) |
| background tasks request | `celery-tasks` | Celery tasks, `.delay()` and the worker |

When creating or editing a skill: name and description in English, exact trigger, and user-facing messages and generated artifacts in pt-BR.

## Repository layout (monorepo)
- `backend/` — FastAPI application and **import root** (packages `apps`, `config`, `core`, `migrations`). Contains `main.py` (`uvicorn main:app`), `manage.py`, `alembic.ini`, `conftest.py`, `pyproject.toml`, `tests/` and `.dockerignore`. It is the build context of the backend image.
- `frontend/` — React + Vite + Mantine (formerly `web/`).
- `tools/` — **dev-only**: `tools/commands/` (`make`/`rm`/`generate` generators), `tools/templates/` (Jinja2) and `tools/paths.py`. It is **not** part of the production image (the build context is `backend/`), so `make:*`/`rm:*`/`generate:*` **do not exist** in the image; `backend/manage.py` registers `tools.commands` only when the folder exists.
- `docker/`, `docs/`, `.github/`, `AGENTS.md`, `CONTRIBUTING.md`, `docker-compose*.yml` and the central `.env` live at the root.
- `tools/paths.py` centralizes `TOOLS_DIR`/`PROJECT_ROOT`/`BACKEND_DIR`/`FRONTEND_DIR`/`TEMPLATES_DIR`, so generation **does not depend on the CWD**.

## Project conventions (language and naming)
- All communication with the user (agent replies, messages, descriptions) is in **Portuguese (pt-BR)**.
- Code comments and docstrings are in **Portuguese**, and so is code documentation (`docs/`, `README.md`, example code blocks). Only identifiers (names of objects and variables) are in English.
- Comments inside skills (`.agents/skills/`) are in **English**, because they are instructions for the agent. Code examples inside skills follow the code rule: comments and docstrings in Portuguese.
- Code identifiers are **strictly English**: file names, functions, methods, classes, variables, constants and parameters.
- Frontend user-facing texts are in **Portuguese**, except established English terms (e.g. "internet", "web", "surf").
- Project name: **Praetor**.
- Skills in `.agents/skills/` are written in **English** (instructions and comments). User-facing texts and generated artifacts (commits, plans) stay in pt-BR.

## Gitflow (branches and commits)
Detailed documentation is in `CONTRIBUTING.md`; the publishing procedure is in the `publish-workflow` skill (triggers `publish` and `publish_production`). Operational summary:
- Model: **full Gitflow**. Long-lived branches: `master` (production, tagged `vX.Y.Z`) and `develop` (integration). **Never** commit directly to them — always go through a Pull Request.
- Supporting branches: `feature/<name>` (from/to `develop`), `bugfix/<name>` (optional, from/to `develop`), `release/<X.Y.Z>` (from `develop`; merged into `master` **and** `develop`, with a tag) and `hotfix/<X.Y.Z>` (from `master`; merged into `master` **and** `develop`, with a tag).
- Feature and hotfix merges use `--no-ff`; delete the branch after merging. Feature/bugfix PRs target `develop`; release/hotfix PRs target `master`.
- Commits follow the **Angular Convention** with a **pt-BR** description and ≤ 72 characters (see `.agents/skills/git-commit/SKILL.md`), e.g. `fix(auth): corrige expiração do token`.
- Required CI before merging: jobs `backend` (`ruff check . ../tools` + `pytest`, from `backend/`), `frontend` (`npm run lint` + `npm run build`, from `frontend/`) and `codegen` (`make:app`/`make:entity` from `backend/` + lint/test of the generated code + frontend build).
- Bootstrap (`develop` already exists locally and remotely; only needed in a new fork): `git branch develop master && git push -u origin develop`.

## Environment setup
- `backend/config/settings.py` requires `DATABASE_URL` and `SECRET_KEY` (no default values). Without them, **any** backend import fails. Run `cp .env.example .env` at the root (the example already points to SQLite at `./default.db`), or export both variables.
- `settings.BASE_DIR` is `backend/`; `env_file` points to the `.env` **at the repository root** (`_PROJECT_ROOT`), the same file Compose reads — do not create a `.env` inside `backend/`.
- The CLI lives in `backend/manage.py` (there is no `manage.py` at the root). Run from `backend/` (`cd backend && python manage.py <cmd>`) or from the root as `python backend/manage.py <cmd>` (both work; no path depends on the CWD).
- For most backend/CLI work this is enough:
  `cd backend && DATABASE_URL="sqlite+aiosqlite:///./dev.db" SECRET_KEY="dev" python3 manage.py <cmd>`

## Commands
Run `python manage.py --help` for the real list. Commands are registered **both** at the root level and inside their group, so `python manage.py db:migrate` and `python manage.py db db:migrate` are equivalent.
- **Ops (runtime)** — in `backend/core/commands/`, also present in the production image:
  - Server: `run:server [--reload]` (uvicorn `main:app`); Worker: `run:worker` (Celery; requires Redis)
  - Database: `db:migrate`, `db:makemigrations -m "msg"`, `db:rollback [--steps N]`, `db:reset`, `db:current`, `db:create`, `db:drop` (procedure in the `database-migrations` skill; `db:reset` has a known defect, see `workspace/changes/audit-fixes/plano_correcoes.md`)
  - Auth/permissions: `auth:createsuperuser`, `auth:makepermissions`; Shell: `shell`
- **Generators (dev-only)** — in `tools/commands/`, absent from the image:
  `make:app <name>`, `make:entity <entity> --app <app>`, `make:command`, `make:middleware`, `rm:app`, `rm:entity`, `generate:schemas <entity> --app <app>`
- Frontend (`frontend/`): `npm install`, `npm run dev`, `npm run build` (`tsc -b && vite build`), `npm run lint`
- Tests: `cd backend && pytest` (as in CI) or `python manage.py run:test [app]`. The `python manage.py test` from the documentation **does not exist**.
- Backend lint: from `backend/`, `ruff check . ../tools` (config in the backend `pyproject.toml`, `dev` extra).
- Dependencies: **all in `backend/pyproject.toml`** — runtime in `[project].dependencies`, and dev/test/generation tools in `[project.optional-dependencies].dev` (`pytest`, `httpx`, `ipython`, `ruff`, `Jinja2`). **There are no `requirements*.txt` files**: from `backend/`, `pip install -e ".[dev]"` (or `pip install .` for runtime only). The project is treated as an **application**, not a package (`[tool.setuptools] packages = []`), so the build installs only dependencies, without copying code. `Jinja2` is **dev-only** (only the generators use it).

## Tests
- CI (`.github/workflows/ci.yml`) has 3 jobs: **backend** (Python 3.12, from `./backend`, `pip install -e ".[dev]"`, `ruff check . ../tools`, `pytest`, with Redis), **frontend** (`npm ci && npm run lint && npm run build`, from `./frontend`) and **codegen** (from `./backend`: `make:app sample` + `make:entity product`, then `ruff check apps/sample` + `pytest apps/sample/tests` and finally `npm run build` in `./frontend`). `cp .env.example .env` runs **at the root** (the `.env` is central).
- `pytest` is configured in `backend/pyproject.toml`: `asyncio_mode = "auto"`, `testpaths = ["tests", "apps"]`, `python_files = ["test_*.py", "*_test.py"]`.
- `conftest.py` lives at **`backend/conftest.py`** (to serve `apps/*/tests`), uses `pytest_asyncio` fixtures + `httpx.AsyncClient`, and a file-based SQLite database with an **absolute path** (`backend/test.db`), creating and dropping tables per test and overriding `get_db`.
- The SQLAlchemy metadata is populated by auto-discovery (`core.utils.auto_discover_apps` imports `apps.<app>.models`), so the tests' `create_all` and `db:create` see the tables.
- Tests generated by `make:entity` are named `test_<entity>.py` and are collected.

## How the application is assembled (auto-discovery)
- Backend apps: any `backend/apps/<name>/` with an `app.py` exporting `app_config` (a `BaseAppConfig`) is registered by `core.utils.auto_discover_apps`. Every `apps/<name>/routers/*.py` exposing an `APIRouter` named `router` is aggregated and mounted at `/api/<name>`; each router adds its own prefix, so endpoints look like `/api/auth/action/login` or `/api/<app>/<entity>`.
- CLI: any `click.Command`/`click.Group` object in `backend/core/commands/*.py` (or in `backend/commands/`) is registered automatically by `manage.py`. `core.utils.auto_discover_commands(cli, base_dir, root=None)` accepts `root` (default `settings.BASE_DIR`) — this is how `manage.py` registers `tools.commands` with `root=PROJECT_ROOT`.
- Permissions: `apps/<name>/permissions/*.py` exporting `DEFINED_PERMISSIONS` are synced by `auth:makepermissions` (the scan starts at `settings.BASE_DIR/"apps"`); endpoints use `require_permission("<entity>:<action>")` (`core/dependencies.py`).
- Frontend routes: `frontend/src/App.tsx` globs `./features/**/routes.tsx`; each file exports an array `*Routes`. Entries automatically get the `/panel` prefix, so a route with `path: '/products'` resolves to `/panel/products` — do not add `/panel` manually.
- Models and migrations: `core.utils.auto_discover_apps` imports each app's `apps.<app>.models` package, which populates the SQLAlchemy metadata (used by `db:create`, the tests and `backend/migrations/env.py`). A model not exported from `apps/<app>/models/__init__.py` is invisible. `backend/migrations/versions/` already contains the initial migration; the canonical path is `db:migrate`.
- Layers: routers → services (`core/base_service.py`) → repositories (`core/base_repository.py`); Pydantic schemas in `apps/<app>/schemas/`.

## Frontend (`frontend/`)
- UI via **Mantine v9** (`@mantine/core` + `@mantine/hooks`). The provider lives in `frontend/src/main.tsx`, together with the CSS imports (`@mantine/core/styles.css`, `@mantine/notifications/styles.css`). PostCSS uses `postcss-preset-mantine` (`frontend/postcss.config.js`). **There is no Tailwind or shadcn/ui** — do not use utility classes.
- Authenticated layout with the Mantine `AppShell` in `frontend/src/App.tsx`; `Sidebar`/`Header` in `frontend/src/components/`.
- Tables: `@tanstack/react-table` rendered by `DataTable` (`frontend/src/components/DataTable.tsx`), which uses Mantine's `<Table>`. Generated templates import `@/components/DataTable`.
- Forms: `react-hook-form` + `@hookform/resolvers` + `zod`. Notifications: `notifications.show` from `@mantine/notifications`. Icons: `lucide-react`.
- UI texts in pt-BR; generic messages in `frontend/src/lib/i18n.ts` (`commonMessages`, `zodMessages`).
- Authentication is **cookie-first**: the backend issues `access_token` (JWT) and `refresh_token` (opaque) in `HttpOnly` cookies, and the JS **never** reads any token (do not use `localStorage`). The SPA state is rebuilt by `AuthProvider` (`frontend/src/features/auth/action/AuthProvider.tsx`) via `GET /auth/action/profile`; on `401`, the axios interceptor (`frontend/src/lib/api.ts`) renews through `/auth/action/refresh` **with no body** (the cookie carries the refresh token). Consume it via `useAuth()` (`frontend/src/lib/auth.ts`).

## Code generation (`make:` / `rm:` / `generate:`)
- Prefer generating over writing by hand (procedure in the `project-codegen` skill). Generators live in **`tools/commands/`** (dev-only) and use `tools/paths.py` to locate `backend/` and `frontend/`, so they run from any directory. `make:entity` creates the backend (model, schema, repository, service, router, permission, test) and the frontend (service, List page, types, zod schema, routes). Flags: `--minimal`, `--only`/`--except` (component subset), `--no-frontend`, `--table-name`, `--no-prefix`.
- The default table name is `<app>_<plural(entity)>`.
- The generated `schemas/<entity>.py` and `types.ts` files are stubs; add the fields, or run `generate:schemas <entity> --app <app>` to rebuild the Pydantic schemas from the SQLAlchemy model.
- Jinja2 templates live in `tools/templates/` (`frontend/` generates Mantine components — `Paper`, `TextInput`, `Button`, `Table` via `DataTable`, `notifications` — and `make:entity` creates `pages/List.tsx`, `pages/Create.tsx`, `pages/Update.tsx` and `components/Form.tsx`, all compiling under `strict`).
- Generated tests are written to `backend/apps/<app>/tests/test_<entity>.py` (collected by `pytest`).
- `make:command`/`make:middleware` write to `backend/commands/` and `backend/middlewares/` (relative to `BACKEND_DIR`).

## Async jobs and background tasks (Celery + Redis)
- **Decision: keep Redis.** It is Celery's *broker*/*result backend* (`CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND`) and it enables **graphical queue management** — via **Flower** (workers, tasks by state, `revoke`, rate limit), the equivalent of Laravel's Horizon. The `redis` service in `docker/compose/base.yml` is intentional, not dead weight.
- Today Celery is configured but there are **no tasks** in the project (`backend/apps/*/tasks.py` are empty stubs); the API **does not** use Redis — only the `worker` consumes the broker. Running `redis` + `worker` is opt-in for whoever uses tasks (procedure in the `celery-tasks` skill).
- **Why not a database queue** (evaluated and rejected):
  - Queue in tables of the application database (SQLAlchemy models + Alembic + a worker with *polling*): more code and more processing cost — with a broker the worker is **blocked** waiting (idle, ~0 CPU), while a database queue pays for *polling* — and it brings no ready-made dashboard.
  - Native Postgres queues (pgqueuer, Procrastinate): low code and no Redis, but **Postgres-only** (dev uses SQLite) and with no ready-made graphical UI.
  - Celery with a Postgres broker (`kombu-pgmq`): removes Redis, but depends on a third-party library and requires the PGMQ extension (Postgres-only).
- **Optional refinement**: to persist/query jobs in the database, switch `CELERY_RESULT_BACKEND` to `db+sqlite:///...` (dev) / `db+postgresql://...` (prod; requires `celery[sqlalchemy]` + a synchronous driver) — Celery creates the `celery_taskmeta`/`celery_tasksetmeta` tables on its own — and add a `flower` service (with `flower` in `pyproject.toml`) to Compose for the dashboard.

## Docker
- **Central** env: a single `.env` at the root for all environments (there is no per-environment `.env`). `backend/config/settings.py` also reads this file when the app runs outside Docker.
- Structure in `docker/` (everything container-related), assembled with Compose `include:`:
  - `docker/compose/base.yml` — shared components (backend `api`/`worker`; infrastructure `redis` and `caddy`, the URL/TLS proxy). **Not** an environment. Note: under `include`, ALL relative paths (context, dockerfile, env_file and volumes) resolve from the folder of the file itself, so files in `docker/compose/` use `../../` to reach the root.
  - `docker/compose/dev.yml` / `docker/compose/prod.yml` — the **environments**; both import `base.yml` and override only what differs.
  - `docker-compose.yml` / `docker-compose.prod.yml` (root) — shortcuts that only import the environments above, so `docker compose up` keeps working from the root. `name` is repeated in them on purpose: Compose **does not** propagate the top-level `name` of an included file.
- Build contexts: `api` uses `context: ../../backend` (the image contains **only** the backend — which is why `tools/` and the generation commands do not exist in production); `frontend` (dev) and `caddy` (prod) use `context: ../../frontend`. `dockerfile:` is resolved **relative to the context**, so the backend references `../docker/Dockerfile.dev` or `../docker/Dockerfile.prod`, and caddy references `../docker/Dockerfile.caddy`.
- In **dev**, `api`/`worker` mount the repository at `/app` (`../../:/app`) and use `working_dir: /app/backend` (where the CLI and `tools/` are visible); an anonymous volume preserves the frontend's `node_modules`.
- Dockerfiles in `docker/`: `Dockerfile.dev`/`Dockerfile.prod` (backend; prod is multi-stage and non-root), `Dockerfile.frontend` (dev) and `Dockerfile.caddy` (prod: SPA bundle build + Caddy runtime). Routes/TLS live in `docker/caddy/Caddyfile.dev`/`Caddyfile.prod`, mounted at `/etc/caddy/Caddyfile` by Compose. The `.dockerignore` files live at the root of each build context: `backend/.dockerignore` and `frontend/.dockerignore`.
- Images install dependencies from `backend/pyproject.toml` (`COPY pyproject.toml` + `pip install .`; the dev image uses `pip install ".[dev]"`, because the bind mount exposes `tools/`), keeping the layer cacheable — **there is no `requirements.txt`** in the build.
- **Configurable identity**: `PROJECT_NAME` (lowercase slug, in `.env`) sets the Compose project name, the images (`<PROJECT_NAME>-api`/`-frontend`/`-caddy`, with `:prod` in production) and therefore the container and network names (`<PROJECT_NAME>_default`). To reuse the boilerplate in another project, change only this variable. There is no custom network — Compose's default network is used.
- Variables reach the containers through `env_file: [../../.env]` (base), with `environment:` overriding only what changes **inside** the network (Celery broker/backend; in prod, `DEBUG` and `DATABASE_URL`). The `migrate` service reads `.env` directly. `config/settings.py` uses `extra="ignore"` to tolerate variables without a field (e.g. `POSTGRES_*`, `PROJECT_NAME`) in the shared `.env`.
- Network exposure: in `dev`, every published port (caddy 8080/8443, api 8000, web 5173, redis 6379) binds to loopback by default (`DEV_BIND_HOST` in `.env` opens it to the network). In production the only entry point is `caddy` (80/443, automatic TLS on `APP_DOMAIN`); the API, the DB and Redis publish no port. The backend trusts `X-Forwarded-*` only from the Compose private networks (`FORWARDED_ALLOW_IPS`), never `*`.
- `build` is declared **only** on `api` and, for the frontend, on `frontend` (dev) and `caddy` (prod); `worker` and `migrate` reuse the image (`<PROJECT_NAME>-api`) to avoid duplicate builds.
- Commands: `docker compose up --build` (dev) and `docker compose -f docker-compose.prod.yml up --build -d` (prod). Requires Docker Compose ≥ 2.20 (because of `include`).
