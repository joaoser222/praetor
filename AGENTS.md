# AGENTS.md

Boilerplate full-stack: backend **FastAPI** (apps modulares, camadas repository/service) e frontend **React 19 + Vite + TypeScript** em `web/`, tudo orquestrado pela CLI Click `manage.py`. Veja `docs/` para a documentação narrativa; este arquivo registra o que não é óbvio a partir dela.

## Convenções do projeto (idioma e nomenclatura)
- Toda comunicação com o usuário (respostas do agente, mensagens, descrições) é em **português (pt-BR)**.
- Comentários e docstrings de código são em **português**.
- Identificadores de código são **estritamente em inglês**: nomes de arquivos, funções, métodos, classes, variáveis, constantes e parâmetros.
- Textos exibidos ao usuário no frontend são em **português**, exceto termos já consagrados em inglês (ex.: "internet", "web", "surf").
- Nome do projeto: **Praetor**.

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

## Realidade dos testes
- CI (`.github/workflows/ci.yml`): Python 3.10, `pip install -r requirements.txt`, `cp .env.example .env`, `pytest`, com um serviço Redis. Dispara em push/PR para `main`/`master`.
- Praticamente não há suíte de testes: o `pytest` na raiz não coleta nada, e `apps/*/tests/*.py` e `tests/` são stubs/placeholders.
- As fixtures estão quebradas como estão: `tests/conftest.py` declara a fixture assíncrona `db` com `@pytest.fixture` (e não `@pytest_asyncio.fixture`) e não há `asyncio_mode` configurado, então testes síncronos que dependem dela falham no modo strict do pytest-asyncio. Além disso, ele fica em `tests/`, então testes gerados em `apps/{app}/tests/` não enxergam `client`/`db`. Corrija os decoradores e/ou adicione um `conftest.py` na raiz ou configuração de pytest antes de confiar nisso.
- `conftest.py` usa SQLite em arquivo (`sqlite+aiosqlite:///./test.db`), cria/derruba todas as tabelas por teste e sobrescreve `get_db`.

## Como a aplicação é montada (auto-descoberta)
- Apps de backend: qualquer `apps/<name>/` com um `app.py` que exporte `app_config` (um `BaseAppConfig`) é registrado por `core.utils.auto_discover_apps`. Todos os `apps/<name>/routers/*.py` que exponham um `APIRouter` chamado `router` são agregados e montados em `/api/<name>`; cada router adiciona seu próprio prefixo, então os endpoints ficam como `/api/auth/action/login` ou `/api/<app>/<entity>`.
- CLI: qualquer objeto `click.Command`/`click.Group` em `core/commands/*.py` (ou em `commands/` na raiz) é registrado automaticamente pelo `manage.py`.
- Permissões: `apps/<name>/permissions/*.py` que exportem `DEFINED_PERMISSIONS` são sincronizadas por `auth:makepermissions`; os endpoints usam `require_permission("<entity>:<action>")` (`core/dependencies.py`).
- Rotas do frontend: `web/src/App.tsx` faz glob de `./features/**/routes.tsx`; cada arquivo exporta um array `*Routes`. As entradas recebem automaticamente o prefixo `/panel`, então uma rota `path: '/products'` resolve para `/panel/products` — não inclua `/panel` manualmente.
- Models e migrações: os metadados do SQLAlchemy só são populados pelas importações em `apps/<app>/models/__init__.py`. O `migrations/env.py` importa cada pacote `apps.<app>.models`, então um model que não esteja nesse `__init__.py` fica invisível para o `db:makemigrations`.
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
- Os templates de frontend em `core/templates/frontend/` geram componentes Mantine (`Paper`, `TextInput`, `Button`, `Table` via `DataTable`, `notifications`).
- ⚠️ Lacuna de geração: o `routes.tsx` gerado importa `./pages/Create` e `./pages/Update`, mas o `make:entity` só escreve `pages/List.tsx`. O `npm run build`/typecheck falha até você adicionar essas páginas (e o `components/Form` que elas importam). Os templates já existem em `core/templates/frontend/` (`create.tsx.j2`, `update.tsx.j2`, `form.tsx.j2`).

## Docker
- Os arquivos de container são exemplos: `docker-compose.example.yml`, `Dockerfile.example`, `Dockerfile.web.example`. O `docker-compose up` do README falha até serem copiados/renomeados. O compose sobrescreve `DATABASE_URL` para SQLite em `./data/database.db`, usa Redis para api/worker, API na 8000 e web na 5173.
