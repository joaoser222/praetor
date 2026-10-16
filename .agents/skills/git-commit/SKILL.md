---
name: git-commit
description: >
  RESTRICTED USE: activate ONLY when user types exactly "commitar" (with
  double 'm' and double 't'). DO NOT activate for "commit", "comitar",
  "fazer commit", "git commit", "git push", "subir", "pronto",
  "finalizar". The only keyword that triggers this skill is the literal
  string "commitar". When activated, it analyzes changed files via git
  diff, groups changes into logical commits following Angular Convention
  with Portuguese descriptions, displays proposed commits with "Aguardando
  confirmacao de commit" and only applies (with git push) after user
  confirmation.
compatibility:
  - git
  - conventional-commits
  - angular-convention
---

# Commit Skill — Praetor

## When to use

Activate this skill **exclusively** when the user types **"commitar"** in
the chat. Do NOT activate for variations like "comitar", "commit",
"fazer commit", "gerar commit", "push". Only the exact string "commitar"
should trigger this skill.

## Prerequisites

- Git configured with `user.name` and `user.email`
- Remote `origin` configured with push permissions
- Previous commits already follow Angular Convention (check history)

## Commit format

```
<tipo>(<escopo>): <descrição em português>
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

### Scope (Praetor modules)

The scope must reflect the affected module or domain area. Use one of the
following (snake_case). For a domain app it should be the app name itself
(`backend/apps/<app>/`, e.g. `auth`).

**Backend domains (`backend/apps/<app>/`):**
- `auth` — Autenticação, sessões cookie-first, tokens, RBAC/permissões
- *any app name* — Apps criados com `make:app <name>` (ex.: `store`)

**Backend transversal (`backend/`):**
- `core` — Base classes, middlewares, utils, Celery, auto-descoberta
- `db` — Migrações Alembic, models, comandos `db:*`
- `config` — `config/settings.py`, database, security, logging

**Frontend (`frontend/`):**
- `frontend` — SPA React/Mantine (features, componentes, rotas, i18n, build)
- `auth` — Fluxo de login/sessão cookie-first do SPA

**Transversal:**
- `docker` — Dockerfiles e Compose (`docker/`)
- `ci` — GitHub Actions (`.github/workflows/`)
- `codegen` — Geradores e templates Jinja2 (`tools/`)
- `deps` — Dependências (`pyproject.toml`)
- `docs` — README, AGENTS.md, CONTRIBUTING.md, `docs/`
- `test` — Suíte de testes quando não pertencer a um app

Use the most specific scope possible. If changes affect multiple contexts,
use the main context scope or create separate commits.

### Description

- **Always in Portuguese (PT-BR)**
- Start with a verb in the present indicative (e.g., "adiciona", "corrige",
  "remove", "atualiza", "refatora", "cria", "implementa")
- Max 72 characters
- Do not start with uppercase
- Do not end with a period

## Execution flow

### Step 1: Analyze changes

Run `git diff --name-status HEAD` to list all modified, added, and deleted
files since the last commit.

Example output:
```
M       backend/apps/auth/services/user.py
A       backend/apps/auth/repositories/token.py
A       backend/migrations/versions/2000b93f04d2_initial_schema.py
M       frontend/src/features/auth/action/service.ts
```

Files already covered by `.gitignore` (`node_modules/`, `dist/`, `venv/`,
`.env`, `*.db`, `__pycache__/`, etc.) never appear in `git diff` and must not
be committed.

### Step 2: Group into logical commits

Analyze the changed files and group them following this logic:

1. **Same module + same type** → one commit
2. **Same module + different types** → separate commits (e.g., one `feat`
   and one `fix` in the same module become two commits)
3. **Different modules** → separate commits per module
4. **Very small changes** (1-2 trivial files) → can be grouped into a single
   commit if part of the same feature
5. **Config/database/frontend infra** → `chore(config)`, `chore(db)`,
   `chore(frontend)`, etc.

Use good judgment: the goal is cohesive commits where each commit is an
atomic logical unit.

For each commit, generate the message in Angular format.

### Step 3: Display proposed commits

Show the user the list of commits to be created:

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

Display the exact message **"Aguardando confirmação de commit"** at the end.

### Step 4: Wait for confirmation

Do NOT run any git commands yet. Only display the proposed commits and
wait for the user to respond.

If the user confirms (e.g., "sim", "pode comitar", "ok", "confirmo",
"vamos"), proceed to Step 5.

If the user rejects or asks for changes (e.g., "não", "espera", "altera
tal commit"), adjust according to feedback and display again.

### Step 5: Apply commits

For each proposed commit (in the order displayed):

1. **Stage the files**:
   ```bash
   git add <file1> <file2> ...
   ```

2. **Create the commit**:
   ```bash
   git commit -m "<tipo>(<escopo>): <descrição>"
   ```

   For commits with a body (when additional justification is needed):
   ```bash
   git commit -m "<tipo>(<escopo>): <descrição>" -m "<body>"
   ```

3. **Only after ALL commits are created**, push:
   ```bash
   git push origin <current-branch>
   ```

   Discover the current branch with `git branch --show-current`.

### Step 6: Report result

After successful push, display:

```
✅ Commits enviados com sucesso para <branch>!
```

If there is an error in any step, display the error message and stop.

## Examples

### Example 1: Simple change in one module (backend)

**Changed files:**
```
M backend/apps/auth/services/user.py
M backend/apps/auth/routers/action.py
M backend/apps/auth/schemas/user.py
A backend/apps/auth/tests/test_user.py
```

**Generated commit:**
```
feat(auth): adiciona revogação de sessão no logout
```

### Example 2: Multiple contexts (backend + frontend)

**Changed files:**
```
M backend/apps/auth/routers/user.py
M backend/apps/auth/schemas/user.py
M frontend/src/features/auth/user/service.ts
M frontend/src/features/auth/user/pages/List.tsx
```

**Generated commits:**
```
1/2: feat(auth): expõe a listagem paginada de usuários
2/2: feat(frontend): consome a listagem paginada no DataTable
```

### Example 3: Fix + chore in the same batch

**Changed files:**
```
M backend/config/security.py
M backend/pyproject.toml
```

**Generated commits:**
```
1/2: fix(config): deriva COOKIE_SECURE de DEBUG quando não definido
2/2: chore(deps): adiciona o ruff ao extra dev
```

## Important rules

- Commit description must be at most **72 characters**
- Use the verb in the **present indicative** in Portuguese ("adiciona",
  not "adicionado")
- Multi-word scopes use snake_case.
- If there is only one changed file and it belongs to a different context
  than expected, use the file's directory context
