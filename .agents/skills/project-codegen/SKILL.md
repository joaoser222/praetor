---
name: project-codegen
description: >
  Use when the user asks to create or remove a Praetor app or entity, to
  generate Pydantic schemas from a model, or to scaffold a command or
  middleware. Covers make:app, make:entity, rm:app, rm:entity,
  generate:schemas, make:command and make:middleware, with their flags and
  the follow-up steps (schema fill-in, permissions sync, migration). Prefer
  these generators over hand-written boilerplate.
compatibility:
  - python 3.12
  - backend/manage.py
---

# Project Codegen — Praetor

## When to use

Use this skill when the user asks to:

- create a new app (a domain under `backend/apps/<name>/`);
- create an entity (a vertical slice: model, schema, repository, service,
  router, permission, test, and frontend pages);
- remove an app or an entity;
- regenerate Pydantic schemas from a SQLAlchemy model;
- scaffold a custom command or middleware.

For migrations, use the `database-migrations` skill. For background tasks,
use the `celery-tasks` skill.

## Hard rules

- **Use the generators first.** Do not hand-write boilerplate that a
  generator produces.
- **The generators are dev-only.** They live in `tools/commands/` and are
  absent from the production image. Run them from the repository, never
  inside the backend image.
- **Run from `backend/`.** Generators resolve paths through
  `tools/paths.py`, so they work from any directory, but `backend/` is the
  documented entry point.
- **Environment variables are required.** Every `manage.py` call needs
  `DATABASE_URL` and `SECRET_KEY`. Use the root `.env` (`cp .env.example .env`
  on a fresh clone) or export them inline.
- Communicate with the user in **Portuguese (pt-BR)**. Identifiers, file and
  folder names stay in **English**.

## Commands

All commands are run from `backend/`:

```bash
cd backend
python manage.py make:app <app_name>
python manage.py make:entity <entity_name> --app <app_name> [flags]
python manage.py rm:app <app_name>
python manage.py rm:entity <entity_name> --app <app_name>
python manage.py generate:schemas <entity_name> --app <app_name>
python manage.py make:command <name>
python manage.py make:middleware <name>
```

Run `python manage.py <command> --help` before using a flag you are not sure
of. The help output is the source of truth.

### `make:app`

Creates the modular app structure in `backend/apps/<app_name>/` and the
matching folder in `frontend/src/features/<app_name>/`. It also generates
`tasks.py` in the app.

### `make:entity` flags

| Flag | Effect |
|------|--------|
| `--app <app>` | Required. The app that owns the entity. |
| `--only model,schema,...` | Generate only the listed components. |
| `--except ...` | Generate everything except the listed components. |
| `--minimal` | Shortcut for `--only model,schema`. |
| `--table-name <name>` | Override the table name. |
| `--no-prefix` | Do not prefix the table name with the app name. |
| `--no-frontend` | Skip all frontend files. |

Components: `model`, `schema`, `repository`, `service`, `router`,
`permission`, `test`.

The default table name is `<app>_<plural(entity)>`.

Backend output in `backend/apps/<app>/`: `models/<entity>.py`,
`schemas/<entity>.py`, `repositories/<entity>.py`, `services/<entity>.py`,
`routers/<entity>.py`, `permissions/<entity>.py`, `tests/test_<entity>.py`.

Frontend output in `frontend/src/features/<app>/<entity>/`: `service.ts`,
`pages/List.tsx` (DataTable), `routes.tsx` (auto-discovered), `schema.ts`
(zod), `types.ts`.

### `rm:app` and `rm:entity`

Remove the backend and frontend folders created by the generator. Confirm
with the user before running either, because removal is not reversible
through the CLI.

### `generate:schemas`

Rebuilds the Pydantic CRUD schemas from the SQLAlchemy model. Use it after
the model changes.

## Follow-up steps after generation

1. **Fill the stubs.** `schemas/<entity>.py` and `types.ts` are generated as
   stubs. Add the real fields, or run `generate:schemas` if the model is the
   source of truth.
2. **Register the model.** The model must be exported from
   `backend/apps/<app>/models/__init__.py`, or it is invisible to the
   metadata used by `db:create`, the tests and `migrations/env.py`.
3. **Permissions.** If the generated `permissions/<entity>.py` defines new
   `DEFINED_PERMISSIONS`, sync them:
   ```bash
   python manage.py auth:makepermissions
   ```
4. **Migration.** Create the migration for the new table with the
   `database-migrations` skill.
5. **Run the tests.** The generated test is collected by pytest:
   ```bash
   cd backend && pytest apps/<app>/tests/test_<entity>.py
   ```
6. **Frontend build** (when frontend was generated):
   ```bash
   cd frontend && npm run build
   ```

## Architecture reminders

- Layers: routers → services (`core/base_service.py`) → repositories
  (`core/base_repository.py`). Schemas are Pydantic, in
  `apps/<app>/schemas/`.
- Endpoints use `require_permission("<entity>:<action>")`
  (`core/dependencies.py`).
- Frontend routes are auto-discovered from `features/**/routes.tsx`, and
  the `/panel` prefix is added automatically. Do not add `/panel` by hand.

## Red flags

- Writing a new entity by hand when `make:entity` can produce it.
- Running `rm:app` or `rm:entity` without user confirmation.
- Leaving schema or type stubs unfilled after generation.
- Creating a model that is not exported from its app's `models/__init__.py`.
- Running generators from inside the production image, where `tools/` is absent.
