# Architecture Overview

PraetorAPI follows a modular, domain-driven architecture designed for high scalability and clear separation of concerns.

## Modular Structure (Apps)

The system is organized into "apps" located in the `apps/` directory. Each app represents a distinct domain (e.g., `auth`, `store`, `billing`).

### Anatomy of a Backend App
- `models/`: Database schema (SQLAlchemy).
- `repositories/`: Data access layer (CRUDS).
- `services/`: Business logic orchestration.
- `schemas/`: Validation and serialization (Pydantic).
- `routers/`: API endpoints (FastAPI).
- `permissions/`: Granular access control definitions.
- `tasks.py`: Background workers (Celery).

## Frontend Architecture

The frontend follows a **Domain-Driven Design (DDD)** approach located in `web/src/features/`.

### Feature Structure (`web/src/features/{app_name}/{entity_name}/`)
Each entity is a self-contained module with its own:
- `pages/`: React views (e.g., `List.tsx` using **DataTable**).
- `routes.tsx`: Local route configuration for the entity.
- `service.ts`: API client (Axios) specifically for this domain.
- `schema.ts`: Frontend validation (Zod) and form types.
- `types.ts`: TypeScript interfaces mirroring backend schemas.

### Component Organization
- `web/src/components/ui/`: Atomic, "raw" components based on **shadcn/ui** patterns (Button, Input, Card, Table). Optimized for CSS-variable-based theming.
- `web/src/components/`: High-level structural components (Sidebar, Header).

### Automatic Route Discovery
The frontend uses Vite's `import.meta.glob` to automatically scan all `features/**/routes.tsx` files. Adding a new feature automatically integrates its routes into the main application and Sidebar without manual registration.

## Layered Design Patterns

### Repository Pattern
Isolates data access through a `BaseRepository`, making the core logic database-agnostic and easier to test.

### Internationalization (i18n)
Translations are handled in a hybrid way:
- `web/src/lib/i18n.ts`: Generic UI strings (Loading, Save, Cancel, etc.) and global Zod messages.
- `web/src/features/**/i18n.ts`: Domain-specific strings.

### Auto-Discovery System
1. **Apps**: Any directory in `apps/` with an `app.py`.
2. **Routers**: Any `APIRouter` named `router` in `routers/*.py`.
3. **Frontend Routes**: Any `routes.tsx` within the `features/` directory.
