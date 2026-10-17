# AGENTS.md

Boilerplate full-stack: backend **FastAPI** (apps modulares, camadas repository/service) em `backend/`, frontend **React 19 + Vite + TypeScript** em `frontend/` e geradores dev-only em `tools/`, tudo orquestrado pela CLI Click `manage.py`. Veja `docs/` para a documentação narrativa; este arquivo registra o que não é óbvio a partir dela.

## Layout do repositório (monorepo)
- `backend/` — aplicação FastAPI e **raiz de importação** (pacotes `apps`, `config`, `core`, `migrations`). Contém `main.py` (`uvicorn main:app`), `manage.py`, `alembic.ini`, `conftest.py`, `pyproject.toml`, `tests/` e `.dockerignore`. É o contexto de build da imagem do backend.
- `frontend/` — React + Vite + Mantine (ex-`web/`).
- `tools/` — **dev-only**: `tools/commands/` (geradores `make`/`rm`/`generate`), `tools/templates/` (Jinja2) e `tools/paths.py`. **Não** entra na imagem de produção (o contexto de build é `backend/`), logo `make:*`/`rm:*`/`generate:*` **não existem** na imagem; `backend/manage.py` só registra `tools.commands` quando a pasta existe.
- `docker/`, `docs/`, `.github/`, `AGENTS.md`, `CONTRIBUTING.md`, `docker-compose*.yml` e o `.env` central ficam na raiz.
- `tools/paths.py` centraliza `TOOLS_DIR`/`PROJECT_ROOT`/`BACKEND_DIR`/`FRONTEND_DIR`/`TEMPLATES_DIR`, então a geração **não depende do CWD**.

## Convenções do projeto (idioma e nomenclatura)
- Toda comunicação com o usuário (respostas do agente, mensagens, descrições) é em **português (pt-BR)**.
- Comentários e docstrings de código são em **português**.
- Identificadores de código são **estritamente em inglês**: nomes de arquivos, funções, métodos, classes, variáveis, constantes e parâmetros.
- Textos exibidos ao usuário no frontend são em **português**, exceto termos já consagrados em inglês (ex.: "internet", "web", "surf").
- Nome do projeto: **Praetor**.

## Gitflow (branches e commits)
Documentação detalhada em `CONTRIBUTING.md`; resumo operacional:
- Modelo: **Gitflow completo**. Branches longevas: `master` (produção, tagueada `vX.Y.Z`) e `develop` (integração). **Nunca** commitar direto nelas — sempre via Pull Request.
- Branches de apoio: `feature/<nome>` (de/para `develop`), `bugfix/<nome>` (opcional, de/para `develop`), `release/<X.Y.Z>` (de `develop`; merge em `master` **e** `develop`, com tag) e `hotfix/<X.Y.Z>` (de `master`; merge em `master` **e** `develop`, com tag).
- Merges de feature/hotfix usam `--no-ff`; apague a branch após o merge. PRs de feature/bugfix miram `develop`; os de release/hotfix miram `master`.
- Commits seguem a **Angular Convention** com descrição em **pt-BR** e ≤ 72 caracteres (ver `.agents/skills/git-commit/SKILL.md`), ex.: `fix(auth): corrige expiração do token`.
- CI obrigatório antes do merge: jobs `backend` (`ruff check . ../tools` + `pytest`, de `backend/`), `frontend` (`npm run lint` + `npm run build`, de `frontend/`) e `codegen` (`make:app`/`make:entity` de `backend/` + lint/test do gerado + build do frontend).
- Bootstrap (a `develop` já existe local e remota; só é preciso num fork novo): `git branch develop master && git push -u origin develop`.

## Configuração do ambiente
- `backend/config/settings.py` exige `DATABASE_URL` e `SECRET_KEY` (sem valores padrão). Sem eles, **qualquer** import do backend falha. Faça `cp .env.example .env` na raiz (o exemplo já aponta para SQLite em `./default.db`), ou exporte as duas variáveis.
- `settings.BASE_DIR` é `backend/`; o `env_file` aponta para o `.env` **na raiz do repositório** (`_PROJECT_ROOT`), o mesmo lido pelo Compose — não recrie um `.env` dentro de `backend/`.
- A CLI vive em `backend/manage.py` (não há `manage.py` na raiz). Rode a partir de `backend/` (`cd backend && python manage.py <cmd>`) ou, da raiz, como `python backend/manage.py <cmd>` (os dois funcionam; nenhum caminho depende do CWD).
- Para a maior parte do trabalho de backend/CLI isto basta:
  `cd backend && DATABASE_URL="sqlite+aiosqlite:///./dev.db" SECRET_KEY="dev" python3 manage.py <cmd>`

## Comandos
Rode `python manage.py --help` para a lista real. Os comandos são registrados **tanto** no nível raiz quanto dentro do seu grupo, então `python manage.py db:migrate` e `python manage.py db db:migrate` são equivalentes.
- **Ops (runtime)** — em `backend/core/commands/`, presentes também na imagem de produção:
  - Servidor: `run:server [--reload]` (uvicorn `main:app`); Worker: `run:worker` (Celery; precisa de Redis)
  - Banco: `db:migrate`, `db:makemigrations -m "msg"`, `db:rollback [--steps N]`, `db:reset`, `db:current`, `db:create`, `db:drop`
  - Auth/permissões: `auth:createsuperuser`, `auth:makepermissions`; Shell: `shell`
- **Geradores (dev-only)** — em `tools/commands/`, ausentes da imagem:
  `make:app <name>`, `make:entity <entity> --app <app>`, `make:command`, `make:middleware`, `rm:app`, `rm:entity`, `generate:schemas <entity> --app <app>`
- Frontend (`frontend/`): `npm install`, `npm run dev`, `npm run build` (`tsc -b && vite build`), `npm run lint`
- Testes: `cd backend && pytest` (como no CI) ou `python manage.py run:test [app]`. O `python manage.py test` da documentação **não existe**.
- Lint de backend: de `backend/`, `ruff check . ../tools` (config no `pyproject.toml` do backend, extra `dev`).
- Dependências: **todas no `backend/pyproject.toml`** — runtime em `[project].dependencies` e ferramentas de dev/teste/geração em `[project.optional-dependencies].dev` (`pytest`, `httpx`, `ipython`, `ruff`, `Jinja2`). **Não há `requirements*.txt`**: de `backend/`, `pip install -e ".[dev]"` (ou `pip install .` para só o runtime). O projeto é tratado como **aplicação**, não como pacote (`[tool.setuptools] packages = []`), então o build instala apenas as dependências, sem copiar o código. `Jinja2` é **dev-only** (só os geradores usam).

## Testes
- CI (`.github/workflows/ci.yml`) tem 3 jobs: **backend** (Python 3.12, de `./backend`, `pip install -e ".[dev]"`, `ruff check . ../tools`, `pytest`, com Redis), **frontend** (`npm ci && npm run lint && npm run build`, de `./frontend`) e **codegen** (de `./backend`: `make:app sample` + `make:entity product`, depois `ruff check apps/sample` + `pytest apps/sample/tests` e, por fim, `npm run build` em `./frontend`). O `cp .env.example .env` roda **na raiz** (o `.env` é central).
- `pytest` é configurado em `backend/pyproject.toml`: `asyncio_mode = "auto"`, `testpaths = ["tests", "apps"]`, `python_files = ["test_*.py", "*_test.py"]`.
- `conftest.py` fica em **`backend/conftest.py`** (para atender `apps/*/tests`), usa fixtures `pytest_asyncio` + `httpx.AsyncClient` e SQLite em arquivo com **caminho absoluto** (`backend/test.db`), criando/derrubando tabelas por teste e sobrescrevendo `get_db`.
- O metadata do SQLAlchemy é populado pela auto-descoberta (`core.utils.auto_discover_apps` importa `apps.<app>.models`), então o `create_all` dos testes e o `db:create` enxergam as tabelas.
- Testes gerados pelo `make:entity` são nomeados `test_<entity>.py` e são coletados.

## Como a aplicação é montada (auto-descoberta)
- Apps de backend: qualquer `backend/apps/<name>/` com um `app.py` que exporte `app_config` (um `BaseAppConfig`) é registrado por `core.utils.auto_discover_apps`. Todos os `apps/<name>/routers/*.py` que exponham um `APIRouter` chamado `router` são agregados e montados em `/api/<name>`; cada router adiciona seu próprio prefixo, então os endpoints ficam como `/api/auth/action/login` ou `/api/<app>/<entity>`.
- CLI: qualquer objeto `click.Command`/`click.Group` em `backend/core/commands/*.py` (ou em `backend/commands/`) é registrado automaticamente pelo `manage.py`. `core.utils.auto_discover_commands(cli, base_dir, root=None)` aceita `root` (padrão `settings.BASE_DIR`) — é assim que `manage.py` registra `tools.commands` com `root=PROJECT_ROOT`.
- Permissões: `apps/<name>/permissions/*.py` que exportem `DEFINED_PERMISSIONS` são sincronizadas por `auth:makepermissions` (a varredura parte de `settings.BASE_DIR/"apps"`); os endpoints usam `require_permission("<entity>:<action>")` (`core/dependencies.py`).
- Rotas do frontend: `frontend/src/App.tsx` faz glob de `./features/**/routes.tsx`; cada arquivo exporta um array `*Routes`. As entradas recebem automaticamente o prefixo `/panel`, então uma rota `path: '/products'` resolve para `/panel/products` — não inclua `/panel` manualmente.
- Models e migrações: `core.utils.auto_discover_apps` importa o pacote `apps.<app>.models` de cada app, o que popula os metadados do SQLAlchemy (usados por `db:create`, pelos testes e pelo `backend/migrations/env.py`). Um model que não esteja no `apps/<app>/models/__init__.py` fica invisível. `backend/migrations/versions/` já contém a migração inicial; o caminho canônico é `db:migrate`.
- Camadas: routers → services (`core/base_service.py`) → repositories (`core/base_repository.py`); schemas Pydantic em `apps/<app>/schemas/`.

## Frontend (`frontend/`)
- UI via **Mantine v9** (`@mantine/core` + `@mantine/hooks`). O provider fica em `frontend/src/main.tsx`, junto com os imports de CSS (`@mantine/core/styles.css`, `@mantine/notifications/styles.css`). O PostCSS usa `postcss-preset-mantine` (`frontend/postcss.config.js`). **Não há Tailwind nem shadcn/ui** — não use classes utilitárias.
- Layout autenticado com `AppShell` do Mantine em `frontend/src/App.tsx`; `Sidebar`/`Header` em `frontend/src/components/`.
- Tabelas: `@tanstack/react-table` renderizado pelo `DataTable` (`frontend/src/components/DataTable.tsx`), que usa `<Table>` do Mantine. Os templates gerados importam `@/components/DataTable`.
- Formulários: `react-hook-form` + `@hookform/resolvers` + `zod`. Notificações: `notifications.show` de `@mantine/notifications`. Ícones: `lucide-react`.
- Textos de UI em pt-BR; mensagens genéricas em `frontend/src/lib/i18n.ts` (`commonMessages`, `zodMessages`).
- Autenticação é **cookie-first**: o backend emite `access_token` (JWT) e `refresh_token` (opaco) em cookies `HttpOnly` e o JS **nunca** lê token algum (não use `localStorage`). O estado do SPA é reconstruído pelo `AuthProvider` (`frontend/src/features/auth/action/AuthProvider.tsx`) via `GET /auth/action/profile`; em `401`, o interceptor do axios (`frontend/src/lib/api.ts`) renova com `/auth/action/refresh` **sem corpo** (o cookie carrega o refresh). Consuma via `useAuth()` (`frontend/src/lib/auth.ts`).

## Geração de código (`make:` / `rm:` / `generate:`)
- Prefira gerar a escrever à mão. Os geradores vivem em **`tools/commands/`** (dev-only) e usam `tools/paths.py` para localizar `backend/` e `frontend/`, então rodam de qualquer diretório. O `make:entity` cria backend (model, schema, repository, service, router, permission, test) e frontend (service, página List, types, schema zod, rotas). Flags: `--minimal`, `--only`/`--except` (subconjunto de componentes), `--no-frontend`, `--table-name`, `--no-prefix`.
- O nome padrão da tabela é `<app>_<plural(entity)>`.
- Os arquivos gerados `schemas/<entity>.py` e `types.ts` são stubs; adicione os campos, ou rode `generate:schemas <entity> --app <app>` para reconstruir os schemas Pydantic a partir do model SQLAlchemy.
- Os templates Jinja2 ficam em `tools/templates/` (`frontend/` gera componentes Mantine — `Paper`, `TextInput`, `Button`, `Table` via `DataTable`, `notifications` — e o `make:entity` cria `pages/List.tsx`, `pages/Create.tsx`, `pages/Update.tsx` e `components/Form.tsx`, todos compilando sob `strict`).
- Os testes gerados são gravados como `backend/apps/<app>/tests/test_<entity>.py` (coletáveis pelo `pytest`).
- `make:command`/`make:middleware` gravam em `backend/commands/` e `backend/middlewares/` (relativos a `BACKEND_DIR`).

## Filas e tarefas assíncronas (Celery + Redis)
- **Decisão: manter o Redis.** Ele é o *broker*/*result backend* do Celery (`CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND`) e é o que habilita a **gestão gráfica** das filas — via **Flower** (workers, tarefas por estado, `revoke`, rate-limit), o equivalente ao Horizon do Laravel. O serviço `redis` em `docker/compose/base.yml` é intencional, não peso morto.
- Hoje o Celery está configurado mas **não há tasks** no projeto (`backend/apps/*/tasks.py` são stubs vazios); a API **não** usa o Redis — só o `worker` consome o broker. Subir `redis` + `worker` é opt-in de quem for usar tarefas.
- **Por que não fila em banco** (avaliado e descartado):
  - Fila em tabelas do próprio banco (models SQLAlchemy + Alembic + worker com *polling*): mais custo de código e de processamento — com broker o worker fica **bloqueado** esperando (ocioso ~0 de CPU), enquanto fila em banco paga *polling* — e não traz dashboard pronto.
  - Filas nativas de Postgres (pgqueuer, Procrastinate): código baixo e sem Redis, porém **Postgres-only** (o dev usa SQLite) e sem UI gráfica pronta.
  - Celery com broker Postgres (`kombu-pgmq`): remove o Redis, mas depende de lib de terceiros e exige a extensão PGMQ (Postgres-only).
- **Refinamento opcional**: para persistir/consultar os jobs no banco, trocar `CELERY_RESULT_BACKEND` para `db+sqlite:///...` (dev) / `db+postgresql://...` (prod; exige `celery[sqlalchemy]` + driver síncrono) — o Celery cria as tabelas `celery_taskmeta`/`celery_tasksetmeta` sozinho — e adicionar um serviço `flower` (com `flower` em `pyproject.toml`) no Compose para o dashboard.

## Docker
- Env **central**: um único `.env` na raiz para todos os ambientes (não há `.env` por ambiente). O `backend/config/settings.py` também lê esse arquivo quando a app roda fora do Docker.
- Estrutura em `docker/` (tudo sobre containers), montada por `include:` do Compose:
  - `docker/compose/base.yml` — componentes compartilhados (backend `api`/`worker`; infra `redis` e `caddy`, o proxy de URLs/TLS). **Não** é um ambiente. Atenção: em `include`, TODOS os caminhos relativos (context, dockerfile, env_file e volumes) resolvem a partir da pasta do próprio arquivo, por isso em `docker/compose/` usam `../../` para chegar à raiz.
  - `docker/compose/dev.yml` / `docker/compose/prod.yml` — os **ambientes**; ambos importam `base.yml` e sobrescrevem só o que difere.
  - `docker-compose.yml` / `docker-compose.prod.yml` (raiz) — atalhos que apenas importam os ambientes acima, para `docker compose up` seguir funcionando da raiz. O `name` é repetido neles de propósito: o Compose **não** propaga o top-level `name` de arquivo incluído.
- Contextos de build: `api` usa `context: ../../backend` (a imagem contém **só** o backend — por isso `tools/` e os comandos de geração não existem em produção); `frontend` (dev) e `caddy` (prod) usam `context: ../../frontend`. O `dockerfile:` é resolvido **relativo ao contexto**, então o backend referencia `../docker/Dockerfile.dev` ou `../docker/Dockerfile.prod`, e o caddy `../docker/Dockerfile.caddy`.
- No **dev**, `api`/`worker` montam o repositório em `/app` (`../../:/app`) e usam `working_dir: /app/backend` (onde a CLI e o `tools/` ficam visíveis); um volume anônimo preserva o `node_modules` do frontend.
- Dockerfiles em `docker/`: `Dockerfile.dev`/`Dockerfile.prod` (backend; o de prod é multi-stage e non-root), `Dockerfile.frontend` (dev) e `Dockerfile.caddy` (prod: build do bundle do SPA + runtime do Caddy). As rotas/TLS ficam em `docker/caddy/Caddyfile.dev`/`Caddyfile.prod`, montados em `/etc/caddy/Caddyfile` pelo Compose. Os `.dockerignore` ficam na raiz do respectivo contexto de build: `backend/.dockerignore` e `frontend/.dockerignore`.
- As imagens instalam as dependências a partir do `backend/pyproject.toml` (`COPY pyproject.toml` + `pip install .`; a imagem de dev usa `pip install ".[dev]"`, porque o bind mount expõe `tools/`), mantendo o layer cacheável — **não há `requirements.txt`** no build.
- **Identidade configurável**: `PROJECT_NAME` (slug em minúsculas, no `.env`) define o nome do projeto Compose, as imagens (`<PROJECT_NAME>-api`/`-frontend`/`-caddy`, com `:prod` em produção) e, por consequência, os nomes de containers e da rede (`<PROJECT_NAME>_default`). Para reaproveitar o boilerplate noutro projeto, basta trocar essa variável. Não há rede customizada — usa-se a rede default do Compose.
- As variáveis chegam aos containers por `env_file: [../../.env]` (base), com `environment:` sobrescrevendo só o que muda **dentro** da rede (broker/back-end do Celery; no prod, `DEBUG` e `DATABASE_URL`). O serviço `migrate` lê o `.env` diretamente. `config/settings.py` usa `extra="ignore"` para tolerar variáveis sem campo (ex.: `POSTGRES_*`, `PROJECT_NAME`) no `.env` compartilhado.
- Endereçamento de rede: no `dev` toda porta publicada (caddy 8080/8443, api 8000, web 5173, redis 6379) fica no loopback por padrão (`DEV_BIND_HOST` no `.env` libera a rede). Em produção o único ponto de entrada é o `caddy` (80/443, TLS automático no `APP_DOMAIN`); a API, o DB e o Redis não publicam porta. O backend confia em `X-Forwarded-*` apenas das redes privadas do compose (`FORWARDED_ALLOW_IPS`), nunca `*`.
- `build` é declarado **apenas** em `api` e, no frontend, em `frontend` (dev) e `caddy` (prod); `worker` e `migrate` reaproveitam a imagem (`<PROJECT_NAME>-api`) para evitar builds duplicados.
- Comandos: `docker compose up --build` (dev) e `docker compose -f docker-compose.prod.yml up --build -d` (prod). Requer Docker Compose ≥ 2.20 (por causa do `include`).
