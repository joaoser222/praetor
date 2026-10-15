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

# Commit Skill — Face Finder

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

### Scope (Face Finder modules)

The scope must reflect the affected module or domain area. Use one of the following (snake_case):

**Backend (api/app/features/):**
- `auth` — Autenticação, sessões, registro
- `collections` — Coleções de fotos, upload ZIP, indexação
- `photos` — Fotos individuais, metadados, faces detectadas
- `searches` — Buscas por rosto de referência, resultados
- `realtime` — SSE, eventos em tempo real

**Frontend (client/src/pages/):**
- `collections` — Páginas de coleções (Index, Item, Form)
- `searches` — Páginas de buscas (Index, Item, Form, SearchCollection)
- `auth` — Login, registro
- `settings` — Configurações do usuário
- `layout` — Layout principal, navegação, toolbar
- `reusables` — Componentes reutilizáveis (ImageGridPage, PhotoDetails, SearchBar, Toolbar, EmptyContainer)

**Transversal:**
- `frontend` — Mudanças gerais no client (build, config, plugins)
- `backend` — Mudanças gerais na api (config, deps, scripts)
- `database` — Migrações, modelos, schemas
- `docker` — docker-compose, Dockerfiles
- `docs` — Documentação (README, AGENTS.md, etc.)
- `tests` — Testes (backend pytest, frontend vitest)
- `config` — Arquivos de configuração (.env.example, pyproject.toml, etc.)

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
M       app/Http/Controllers/ClientController.php
A       app/Models/Client.php
A       database/migrations/2026_07_31_000001_create_clients_table.php
M       resources/js/pages/clients/Details.vue
```

Files already covered by `.gitignore` (`vendor/`, `node_modules/`,
`public/build`, `.env`, etc.) never appear in `git diff` and must not be
committed.

### Step 2: Group into logical commits

Analyze the changed files and group them following this logic:

1. **Same module + same type** → one commit
2. **Same module + different types** → separate commits (e.g., one `feat`
   and one `fix` in the same module become two commits)
3. **Different modules** → separate commits per module
4. **Very small changes** (1-2 trivial files) → can be grouped into a single
   commit if part of the same feature
5. **Config/database/frontend infra** → `chore(config)`, `chore(database)`,
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

1/3: feat(collections): adiciona validação de tamanho máximo do zip
  Files:
    M api/app/features/collections/service.py
    M api/app/features/collections/router.py
    M api/app/features/collections/schemas.py
    A api/tests/features/collections/test_service.py

2/3: feat(searches): implementa filtro por tolerância na busca
  Files:
    M api/app/features/searches/service.py
    M api/app/features/searches/router.py
    M client/src/pages/searches/Item.vue
    M client/src/pages/searches/Form.vue

3/3: chore(frontend): remove importação desnecessária de roboto-fontface
  Files:
    M client/src/plugins/vuetify.js

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
M api/app/features/collections/service.py
M api/app/features/collections/router.py
M api/app/features/collections/schemas.py
A api/tests/features/collections/test_service.py
```

**Generated commit:**
```
feat(collections): adiciona validação de tamanho máximo do ZIP
```

### Example 2: Multiple contexts (backend + frontend)

**Changed files:**
```
M api/app/features/searches/service.py
M api/app/features/searches/router.py
M client/src/pages/searches/Item.vue
M client/src/pages/searches/Form.vue
```

**Generated commits:**
```
1/2: feat(searches): implementa filtro por tolerância na busca
2/2: feat(frontend): adiciona slider de tolerância na página de busca
```

### Example 3: Fix + chore in the same batch

**Changed files:**
```
M api/app/shared/services/recognition.py
M client/src/plugins/vuetify.js
```

**Generated commits:**
```
1/2: fix(recognition): corrige ordenação de verificação de arquivo nulo
2/2: chore(frontend): remove importação desnecessária de roboto-fontface
```

## Important rules

- Commit description must be at most **72 characters**
- Use the verb in the **present indicative** in Portuguese ("adiciona",
  not "adicionado")
- Multi-word scopes use snake_case: `gateway_payments`,
  `financial_categories`
- If there is only one changed file and it belongs to a different context
  than expected, use the file's directory context
