# Architecture Overview

Praetor follows a modular, domain-driven architecture designed for high scalability and clear separation of concerns.

## Repository Layout

```
backend/     # FastAPI app — the import root (apps/, core/, config/, migrations/)
frontend/    # React + Vite + Mantine SPA
tools/       # Code generators (dev-only: commands + Jinja2 templates)
docker/      # Dockerfiles and Compose definitions (base/develop/production)
```

`backend/` is self-contained: `uvicorn main:app` and `backend/manage.py` run from there, and the packages `apps`, `core` and `config` live inside it. The generators in `tools/` are **not** part of the production image (the backend build context is `backend/`), so `make:*`, `rm:*` and `generate:*` only exist when the repository is checked out.

## Modular Structure (Apps)

The system is organized into "apps" located in the `backend/apps/` directory. Each app represents a distinct domain (e.g., `auth`, `store`, `billing`).

### Anatomy of a Backend App
- `models/`: Database schema (SQLAlchemy).
- `repositories/`: Data access layer (CRUDS).
- `services/`: Business logic orchestration.
- `schemas/`: Validation and serialization (Pydantic).
- `routers/`: API endpoints (FastAPI).
- `permissions/`: Granular access control definitions.
- `tasks.py`: Background workers (Celery).

## Frontend Architecture

The frontend follows a **Domain-Driven Design (DDD)** approach located in `frontend/src/features/`.

### Feature Structure (`frontend/src/features/{app_name}/{entity_name}/`)
Each entity is a self-contained module with its own:
- `pages/`: React views (e.g., `List.tsx` using **DataTable**).
- `routes.tsx`: Local route configuration for the entity.
- `service.ts`: API client (Axios) specifically for this domain.
- `schema.ts`: Frontend validation (Zod) and form types.
- `types.ts`: TypeScript interfaces mirroring backend schemas.

### Component Organization
- UI: **Mantine v9** components (`@mantine/core`, `@mantine/hooks`), configured via `MantineProvider` in `frontend/src/main.tsx`.
- `frontend/src/components/`: `DataTable` (**TanStack Table** rendered with Mantine's `Table`) and layout components (`Sidebar`, `Header`; `AppShell` in `App.tsx`).

### Automatic Route Discovery
The frontend uses Vite's `import.meta.glob` to automatically scan all `features/**/routes.tsx` files. Adding a new feature automatically integrates its routes into the main application and Sidebar without manual registration.

## Layered Design Patterns

### Repository Pattern
Isolates data access through a `BaseRepository`, making the core logic database-agnostic and easier to test.

### Internationalization (i18n)
Translations are handled in a hybrid way:
- `frontend/src/lib/i18n.ts`: Generic UI strings (Loading, Save, Cancel, etc.) and global Zod messages.
- `frontend/src/features/**/i18n.ts`: Domain-specific strings.

### Auto-Discovery System
1. **Apps**: Any directory in `backend/apps/` with an `app.py`.
2. **Routers**: Any `APIRouter` named `router` in `routers/*.py`.
3. **Frontend Routes**: Any `routes.tsx` within the `features/` directory.
