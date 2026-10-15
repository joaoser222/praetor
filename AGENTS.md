# AGENTS.md

Boilerplate full-stack: backend **FastAPI** (apps modulares, camadas repository/service) e frontend **React 19 + Vite + TypeScript** em `web/`, tudo orquestrado pela CLI Click `manage.py`. Veja `docs/` para a documentação narrativa; este arquivo registra o que não é óbvio a partir dela.

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
- CI obrigatório antes do merge: jobs `backend` (`ruff check .` + `pytest`), `frontend` (`npm run lint` + `npm run build`) e `codegen` (`make:app`/`make:entity` + build).
- Bootstrap (a branch `develop` ainda não existe): `git branch develop master && git push -u origin develop`.

## Configuração do ambiente
- `config/settings.py` exige `DATABASE_URL` e `SECRET_KEY` (sem valores padrão). Sem eles, **qualquer** import do backend falha. Faça `cp .env.example .env` (o exemplo já aponta para SQLite em `./default.db`), ou exporte as duas variáveis.
- Para a maior parte do trabalho de backend/CLI isto basta:
  `DATABASE_URL="sqlite+aiosqlite:///./dev.db" SECRET_KEY="dev" python3 manage.py <cmd>`

## Comandos
Rode `python manage.py --help` para a lista real. Os comandos são registrados **tanto** no nível raiz quanto dentro do seu grupo, então `python manage.py db:migrate` e `python manage.py db db:migrate` são equivalentes.
- Servidor: `python manage.py run:server [--reload]` (uvicorn `main:app`)
- Banco: `db:migrate`, `db:makemigrations -m "msg"`, `db:rollback [--steps N]`, `db:reset`, `db:current`, `db:create`, `db:drop`
- Auth/permissões: `auth:createsuperuser`, `auth:makepermissions`
- Geradores: `make:app <name>`, `make:entity <entity> --app <app>`, `make:command`, `make:middleware`, `rm:app`, `rm:entity`, `generate:schemas <entity> --app <app>`
- Worker: `python manage.py run:worker` (Celery; precisa de Redis)
- Frontend (`web/`): `npm install`, `npm run dev`, `npm run build` (`tsc -b && vite build`), `npm run lint`
- Testes: `pytest` (como no CI) ou `python manage.py run:test [app]`. O `python manage.py test` da documentação **não existe**.
- Lint de backend: `ruff check .` (config em `pyproject.toml`; `ruff` está em `requirements-dev.txt`).
- Dependências: runtime em `requirements.txt`, ferramentas de dev/teste em `requirements-dev.txt` (`-r requirements.txt` + `pytest`, `httpx`, `ruff`, `ipython`).

## Testes
- CI (`.github/workflows/ci.yml`) tem 3 jobs: **backend** (Python 3.12, `pip install -r requirements-dev.txt`, `ruff check .`, `pytest`, com Redis), **frontend** (`npm ci && npm run lint && npm run build`) e **codegen** (roda `make:app sample` + `make:entity product` e depois `npm run build` no `web/`).
- `pytest` é configurado em `pyproject.toml`: `asyncio_mode = "auto"`, `testpaths = ["tests", "apps"]`, `python_files = ["test_*.py", "*_test.py"]`.
- `conftest.py` fica **na raiz** (para atender `apps/*/tests`), usa fixtures `pytest_asyncio` + `httpx.AsyncClient` e SQLite em arquivo (`./test.db`), criando/derrubando tabelas por teste e sobrescrevendo `get_db`.
- O metadata do SQLAlchemy é populado pela auto-descoberta (`core.utils.auto_discover_apps` importa `apps.<app>.models`), então o `create_all` dos testes e o `db:create` enxergam as tabelas.
- Testes gerados pelo `make:entity` são nomeados `test_<entity>.py` e são coletados.

## Como a aplicação é montada (auto-descoberta)
- Apps de backend: qualquer `apps/<name>/` com um `app.py` que exporte `app_config` (um `BaseAppConfig`) é registrado por `core.utils.auto_discover_apps`. Todos os `apps/<name>/routers/*.py` que exponham um `APIRouter` chamado `router` são agregados e montados em `/api/<name>`; cada router adiciona seu próprio prefixo, então os endpoints ficam como `/api/auth/action/login` ou `/api/<app>/<entity>`.
- CLI: qualquer objeto `click.Command`/`click.Group` em `core/commands/*.py` (ou em `commands/` na raiz) é registrado automaticamente pelo `manage.py`.
- Permissões: `apps/<name>/permissions/*.py` que exportem `DEFINED_PERMISSIONS` são sincronizadas por `auth:makepermissions`; os endpoints usam `require_permission("<entity>:<action>")` (`core/dependencies.py`).
- Rotas do frontend: `web/src/App.tsx` faz glob de `./features/**/routes.tsx`; cada arquivo exporta um array `*Routes`. As entradas recebem automaticamente o prefixo `/panel`, então uma rota `path: '/products'` resolve para `/panel/products` — não inclua `/panel` manualmente.
- Models e migrações: `core.utils.auto_discover_apps` importa o pacote `apps.<app>.models` de cada app, o que popula os metadados do SQLAlchemy (usados por `db:create`, pelos testes e pelo `migrations/env.py`). Um model que não esteja no `apps/<app>/models/__init__.py` fica invisível. `migrations/versions/` já contém a migração inicial; o caminho canônico é `db:migrate`.
- Camadas: routers → services (`core/base_service.py`) → repositories (`core/base_repository.py`); schemas Pydantic em `apps/<app>/schemas/`.

## Frontend (`web/`)
- UI via **Mantine v9** (`@mantine/core` + `@mantine/hooks`). O provider fica em `web/src/main.tsx`, junto com os imports de CSS (`@mantine/core/styles.css`, `@mantine/notifications/styles.css`). O PostCSS usa `postcss-preset-mantine` (`web/postcss.config.js`). **Não há Tailwind nem shadcn/ui** — não use classes utilitárias.
- Layout autenticado com `AppShell` do Mantine em `web/src/App.tsx`; `Sidebar`/`Header` em `web/src/components/`.
- Tabelas: `@tanstack/react-table` renderizado pelo `DataTable` (`web/src/components/DataTable.tsx`), que usa `<Table>` do Mantine. Os templates gerados importam `@/components/DataTable`.
- Formulários: `react-hook-form` + `@hookform/resolvers` + `zod`. Notificações: `notifications.show` de `@mantine/notifications`. Ícones: `lucide-react`.
- Textos de UI em pt-BR; mensagens genéricas em `web/src/lib/i18n.ts` (`commonMessages`, `zodMessages`).

## Geração de código (`make:`)
- Prefira gerar a escrever à mão. O `make:entity` cria backend (model, schema, repository, service, router, permission, test) e frontend (service, página List, types, schema zod, rotas). Flags: `--minimal`, `--only`/`--except` (subconjunto de componentes), `--no-frontend`, `--table-name`, `--no-prefix`.
- O nome padrão da tabela é `<app>_<plural(entity)>`.
- Os arquivos gerados `schemas/<entity>.py` e `types.ts` são stubs; adicione os campos, ou rode `generate:schemas <entity> --app <app>` para reconstruir os schemas Pydantic a partir do model SQLAlchemy.
- Os templates de frontend em `core/templates/frontend/` geram componentes Mantine (`Paper`, `TextInput`, `Button`, `Table` via `DataTable`, `notifications`) e o `make:entity` cria `pages/List.tsx`, `pages/Create.tsx`, `pages/Update.tsx` e `components/Form.tsx` — todos compilam sob `strict`.
- Os testes gerados são gravados como `apps/<app>/tests/test_<entity>.py` (coletáveis pelo `pytest`).

## Docker
- Os arquivos de container são exemplos: `docker-compose.example.yml`, `Dockerfile.example`, `Dockerfile.web.example`. O `docker-compose up` do README falha até serem copiados/renomeados. O compose sobrescreve `DATABASE_URL` para SQLite em `./data/database.db`, usa Redis para api/worker, API na 8000 e web na 5173.
