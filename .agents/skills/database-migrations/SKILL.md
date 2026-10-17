---
name: database-migrations
description: >
  Use when the user asks to create, apply, roll back, inspect or reset
  database migrations or tables in Praetor. Covers db:makemigrations,
  db:migrate, db:rollback, db:current, db:history, db:create and db:drop,
  and states which command is canonical. Warns about db:reset until its
  known bug is fixed.
compatibility:
  - python 3.12
  - alembic
  - sqlalchemy 2
---

# Database Migrations — Praetor

## When to use

Use this skill when the user asks to:

- create a migration after a model changed;
- apply or roll back migrations;
- check the current revision or the history;
- create or drop tables directly for quick local development;
- reset the database.

For creating the model itself, use `project-codegen`.

## Hard rules

- **`db:migrate` is the canonical way** to bring the schema up. Migrations
  are versioned in `backend/migrations/versions/`. The project ships the
  initial migration.
- **`db:create` is for quick local work only.** It creates tables from the
  models and does not write migration history. Do not use it on a database
  that will be shared or migrated later.
- **Models must be registered.** A model is seen by Alembic only if it is
  exported from `backend/apps/<app>/models/__init__.py`.
- **Ask before destructive commands.** `db:drop` and `db:reset` delete data.
  Confirm with the user and state the database URL first.
- **Do not use `db:reset` as a reset.** It leaves the database without
  tables while Alembic still reports `head`, so a later `db:migrate` does
  nothing. This is a known defect (`workspace/changes/audit-fixes/plano_correcoes.md`, item 2). Until
  it is fixed, reset by dropping and re-running `db:migrate` on a fresh
  database file, after confirming with the user.
- Communicate with the user in **Portuguese (pt-BR)**.

## Commands

Run from `backend/`:

```bash
cd backend
python manage.py db:makemigrations -m "short description"
python manage.py db:migrate
python manage.py db:rollback [--steps N]
python manage.py db:current
python manage.py db:history
python manage.py db:create      # quick dev only, no history
python manage.py db:drop        # destructive
```

The commands are registered both at the root and inside the `db` group, so
`python manage.py db db:migrate` is equivalent to `python manage.py db:migrate`.

The environment must define `DATABASE_URL` and `SECRET_KEY`. For local
work without a `.env`:

```bash
cd backend
DATABASE_URL="sqlite+aiosqlite:///./dev.db" SECRET_KEY="dev" python manage.py db:migrate
```

## Workflow: change a model

1. Edit the model in `backend/apps/<app>/models/<entity>.py` and confirm it
   is exported from `models/__init__.py`.
2. Create the migration with a clear message:
   ```bash
   python manage.py db:makemigrations -m "adiciona coluna price em product"
   ```
3. Read the generated file in `backend/migrations/versions/` and check the
   operations. Autogenerate does not detect every change (renames, some
   type changes), so review it by hand.
4. Apply it:
   ```bash
   python manage.py db:migrate
   ```
5. Run the tests:
   ```bash
   cd backend && pytest
   ```

## Workflow: roll back

1. Check the current revision: `python manage.py db:current`.
2. Roll back one step, or N steps:
   ```bash
   python manage.py db:rollback --steps 1
   ```
3. Confirm the state with `db:current` again.

## Production

- Production runs migrations through the `migrate` service of
  `docker/compose/prod.yml`, which applies `db:migrate` and exits before the
  API and worker start. Do not run migrations by hand in production unless
  the user asks.
- The production database is PostgreSQL. A migration that works on SQLite
  can still fail there, so check it against PostgreSQL when the change is
  not trivial.

## Red flags

- Using `db:create` on a database that also uses migrations.
- Editing a migration that has already been applied, instead of adding a new one.
- Running `db:drop` or `db:reset` without confirmation.
- Trusting autogenerate without reading the migration file.
- Creating a model that is not registered in its app's `models/__init__.py`.
