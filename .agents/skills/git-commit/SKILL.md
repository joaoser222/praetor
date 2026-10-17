---
name: git-commit
description: >
  RESTRICTED USE: activate ONLY when the user types exactly "commit" (the
  single lowercase word). DO NOT activate for "commitar", "comitar", "make a
  commit", "git commit", "git push", "push", "ship it", "done" or any other
  variation. When activated, it analyzes the changed files with git diff,
  groups them into logical commits following the Angular Convention with
  Portuguese descriptions, shows the proposed commits ending with "Aguardando
  confirmação de commit", and only stages, commits and pushes after the user
  confirms.
compatibility:
  - git
  - conventional-commits
  - angular-convention
---

# Commit Skill — Praetor

## When to use

Activate this skill **exclusively** when the user types the exact word
**`commit`** in the chat. Any other wording does not activate it.

## Prerequisites

- Git configured with `user.name` and `user.email`.
- Remote `origin` configured with push permissions.
- Previous commits already follow the Angular Convention (check the history
  with `git log --oneline -20` if unsure).

## Hard rules

- **Never commit or push to `master` or `develop`.** If the current branch is
  one of them, stop and tell the user to switch to a `feature/*` or
  `bugfix/*` branch. Use the `publish-workflow` skill to deliver the work.
- **Show the plan before running any write command.** No `git add`,
  `git commit` or `git push` until the user confirms.
- Communicate with the user in **Portuguese (pt-BR)**. Commit descriptions
  are in **Portuguese (pt-BR)**.

## Commit format

```
<type>(<scope>): <description in Portuguese>
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code refactoring with no behavior change |
| `chore` | Infrastructure, CLI, config, build tasks |
| `docs` | Documentation |
| `test` | Tests |
| `style` | Code formatting, linting |

### Scope

The scope reflects the affected module or domain area, in snake_case. For a
domain app it is the app name itself (`backend/apps/<app>/`, for example
`auth`).

**Backend domains (`backend/apps/<app>/`):**
- `auth` — authentication, cookie-first sessions, tokens, RBAC/permissions
- *any app name* — apps created with `make:app <name>` (for example `store`)

**Backend cross-cutting (`backend/`):**
- `core` — base classes, middlewares, utils, Celery, auto-discovery
- `db` — Alembic migrations, models, `db:*` commands
- `config` — `config/settings.py`, database, security, logging

**Frontend (`frontend/`):**
- `frontend` — React/Mantine SPA (features, components, routes, i18n, build)
- `auth` — login and cookie-first session flow in the SPA

**Cross-cutting:**
- `docker` — Dockerfiles and Compose (`docker/`)
- `ci` — GitHub Actions (`.github/workflows/`)
- `codegen` — generators and Jinja2 templates (`tools/`)
- `deps` — dependencies (`pyproject.toml`)
- `docs` — README, AGENTS.md, CONTRIBUTING.md, `docs/`, skills in `.agents/`
- `test` — test suite when it does not belong to a single app

Use the most specific scope possible. If changes span several contexts, use
the main context or split them into separate commits.

### Description

- **Always in Portuguese (pt-BR).**
- Start with a verb in the present indicative: "adiciona", "corrige",
  "remove", "atualiza", "refatora", "cria", "implementa". Not "adicionado".
- At most **72 characters**.
- Lowercase first letter. No trailing period.

## Execution flow

### Step 1: Analyze changes

Run `git status --short` and `git diff --name-status HEAD` to list the
modified, added, deleted and untracked files. Files already covered by
`.gitignore` (`node_modules/`, `dist/`, `venv/`, `.env`, `*.db`,
`__pycache__/`, `workspace/`, and so on) must never be committed.

For renames, git shows `D` and `A` until the old and new paths are staged
together. Stage both in the same commit so git records the rename.

### Step 2: Group into logical commits

1. **Same module and same type** → one commit.
2. **Same module and different types** → separate commits (for example one
   `feat` and one `fix` become two commits).
3. **Different modules** → one commit per module.
4. **Very small related changes** (one or two trivial files of the same
   feature) → may share one commit.
5. **Config, database and frontend infrastructure** → `chore(config)`,
   `chore(db)`, `chore(frontend)`, and so on.

The goal is cohesive, atomic commits.

### Step 3: Show the proposed commits

Present the list in this format (the layout and the closing line stay in
Portuguese, because they are shown to the user):

```
========================================
🤖 Proposed commits:
========================================

1/3: feat(auth): revoga o refresh token no logout
  Files:
    M backend/apps/auth/services/user.py
    M backend/apps/auth/routers/action.py
    A backend/tests/test_auth_flow.py

2/3: feat(frontend): limpa o estado do SPA ao encerrar a sessão
  Files:
    M frontend/src/features/auth/action/service.ts
    M frontend/src/features/auth/action/AuthProvider.tsx

3/3: chore(deps): move o Jinja2 para o extra dev
  Files:
    M backend/pyproject.toml

========================================
Aguardando confirmação de commit
========================================
```

End the message with the exact sentence **"Aguardando confirmação de commit"**.

### Step 4: Wait for confirmation

Run no write command in this step. If the user confirms (for example "sim",
"pode commitar", "ok", "confirmo", "vamos"), go to Step 5. If the user rejects
or asks for changes ("não", "espera", "altera tal commit"), adjust the plan
and show it again.

### Step 5: Apply the commits

For each proposed commit, in the order shown:

1. Stage exactly the listed files:
   ```bash
   git add <file1> <file2> ...
   ```
2. Create the commit:
   ```bash
   git commit -m "<type>(<scope>): <description>"
   ```
   When a body is needed to justify the change:
   ```bash
   git commit -m "<type>(<scope>): <description>" -m "<body>"
   ```

Push only **after all commits are created**:

```bash
git push origin "$(git branch --show-current)"
```

### Step 6: Report the result

After a successful push, report in Portuguese:

```
✅ Commits enviados com sucesso para <branch>!
```

If any step fails, show the error and stop. Do not retry with `--force` or
`--no-verify`.

## Examples

### Example 1: One module (backend)

Changed files:
```
M backend/apps/auth/services/user.py
M backend/apps/auth/routers/action.py
M backend/apps/auth/schemas/user.py
A backend/apps/auth/tests/test_user.py
```

Generated commit:
```
feat(auth): adiciona revogação de sessão no logout
```

### Example 2: Backend and frontend

Changed files:
```
M backend/apps/auth/routers/user.py
M backend/apps/auth/schemas/user.py
M frontend/src/features/auth/user/service.ts
M frontend/src/features/auth/user/pages/List.tsx
```

Generated commits:
```
1/2: feat(auth): expõe a listagem paginada de usuários
2/2: feat(frontend): consome a listagem paginada no DataTable
```

### Example 3: Fix and chore in the same batch

Changed files:
```
M backend/config/security.py
M backend/pyproject.toml
```

Generated commits:
```
1/2: fix(config): deriva COOKIE_SECURE de DEBUG quando não definido
2/2: chore(deps): adiciona o ruff ao extra dev
```

## Red flags

- Staging or committing before the user confirmed the plan.
- Committing to `master` or `develop`.
- Committing `.env`, databases, caches or anything listed in `.gitignore`.
- Descriptions longer than 72 characters, or written in English.
- Pushing before every commit of the batch is created.
