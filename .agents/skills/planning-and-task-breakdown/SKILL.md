---
name: planning-and-task-breakdown
description: >
  RESTRICTED USE: activate ONLY when the user types exactly "planner" (the
  single word). DO NOT activate for "plan", "planejar", "planning",
  "breakdown", "tasks" or any other variation. When activated, it plans a NEW
  feature: it asks the clarifying questions needed to understand the request,
  investigates the codebase in read-only mode, and writes an ordered, detailed
  plan to workspace/changes/<change>/plan.md. When the user later types exactly
  "apply", it starts executing the planned work, but ONLY if every open
  question has been resolved. Never writes product code during planning.
compatibility:
  - markdown
---

# Planning and Task Breakdown — Praetor

## When to use

Activate this skill **exclusively** when the user types **`planner`** in the
chat. Do NOT activate for variations such as "plan", "planejar",
"planning", "breakdown" or "tasks". Only the exact word starts a planning
session.

The matching execution keyword is **`apply`**. Only the exact word starts
executing an already written plan (see [The `apply` gate](#the-apply-gate)).

If the user types `apply` but no plan exists, do not invent one. Tell the
user to run `planner` first.

## Hard rules

- **No product code while planning.** Planning is read-only: read the request,
  the codebase and the conventions. Do not create, edit or delete product
  source, tests, migrations or configuration. The only file written during
  planning is the plan itself and the workspace bookkeeping files.
- **Ask before assuming.** If the request is ambiguous, ask. Never fill gaps
  with guesses.
- **Discover conventions, never invent them.** Derive naming, structure and
  patterns from `AGENTS.md`, `CONTRIBUTING.md`, `docs/`, the configuration
  files and the existing code. If a convention is not evident, treat it as an
  open question.
- **Never execute with open questions.** `apply` runs only when the plan has
  no unresolved questions.
- **Bootstrap the workspace idempotently.** Create only what is missing and
  never overwrite existing workspace files.
- **Prefer a single task.** Split a change into several tasks only when there
  is an explicit reason (see [Task granularity](#task-granularity)).
- Communicate with the user in **Portuguese (pt-BR)**. Code identifiers, file
  names and the change slug stay in **English**.

## Phase 0: Bootstrap and resume

On every `planner` run, prepare the workspace idempotently:

```text
workspace/
├── LAST_SESSION.md      # continuity between sessions
├── TODO.md              # cross-change backlog
└── changes/             # one folder per change
```

- If a file or directory already exists, leave it untouched.
- Make sure `workspace/` is ignored by Git. If `.gitignore` does not ignore
  it, add a `workspace/` line. Never duplicate the entry and never touch
  unrelated rules.
- If `workspace/LAST_SESSION.md` exists, read it first to recover the
  previous session before asking anything.

## Phase 1: Understand the request

Read the request carefully and identify what is missing to plan correctly.
Ask the user, in Portuguese, the questions needed to close those gaps. Keep
asking until the answers are concrete. Do not build a plan on unknowns.

Typical points to clarify:

- **Goal:** what behavior must become true, and for whom?
- **Scope:** which app or feature (`apps/<app>/`), backend only, frontend
  only, or both?
- **Data:** new model or entity? Fields, relations, table name? Does it need
  a migration?
- **API:** which endpoints, verbs, payloads and permissions
  (`<entity>:<action>`)?
- **UI:** new page or route, list, create, update, forms, validation?
- **Auth and permissions:** who can do it?
- **Edge cases:** empty states, errors, limits, idempotency.
- **Out of scope:** what explicitly will NOT be built.

Record every question in the plan's **Perguntas abertas** section. A question
is resolved only when the user gave an answer that removes the ambiguity.

If an answer moves something out of scope, do not drop it silently. Record it
in `workspace/TODO.md` as future work.

## Phase 2: Investigate (read-only)

Walk the codebase to ground the plan in the real conventions and to name the
exact files that will change. If a rule is not evident in `AGENTS.md`, the
configuration or the existing code, ask about it.

Useful entry points:

- `AGENTS.md`, `CONTRIBUTING.md` and `docs/` for conventions.
- `backend/apps/<app>/` for models, schemas, repositories, services, routers,
  permissions and tests.
- `frontend/src/features/<feature>/` for services, pages, routes and zod
  schemas.
- Prefer the generators (`make:app`, `make:entity`, `generate:schemas`) over
  hand-written boilerplate. The `project-codegen` skill documents them.

Identify the existing patterns to follow, the dependencies between components,
and the risks. Do not run commands that change state.

## Phase 3: Dependency order and slicing

Map what depends on what and plan bottom-up, foundations first. Prefer
**vertical slices**: one complete, testable path (schema, API and UI) instead
of "all the database, then all the API, then all the UI".

```
Database schema / model
    └── Schemas (Pydantic / zod)
            ├── Repository → Service
            │        └── Router / endpoint
            │                └── Frontend service → UI
            └── Permissions
    └── Migration
```

## Task granularity

**Default: one task.** A change is normally a single task whose steps live
inline in `plan.md`. Do not split by reflex.

Split into several tasks only when at least one of these is true:

- The work spans more than one focused session.
- It touches two or more independent subsystems (for example auth and billing).
- Parts must run in a defined order or can be parallelized safely.
- The acceptance criteria do not fit in about three bullet points.
- The task title would need the word "and".

When splitting, keep each task Small or Medium and create the per-task files
described in [Splitting into `tasks/`](#splitting-into-tasks). Never split just
to look organized.

| Size | Files | Scope | Example |
|------|-------|-------|---------|
| **XS** | 1 | one function or config change | add a validation rule |
| **S** | 1-2 | one component or endpoint | add an API endpoint |
| **M** | 3-5 | one feature slice | registration flow |
| **L** | 5-8 | multi-component feature | search with filters and pagination |
| **XL** | 8+ | **too large, split it** | none |

## Output: the plan file

```text
workspace/
├── LAST_SESSION.md            # continuity between sessions (maintained)
├── TODO.md                    # cross-change backlog (maintained)
└── changes/
    └── <change-slug>/
        ├── plan.md            # always: overview, open questions, ordered plan
        └── tasks/             # only when the change was split
            ├── 01-<slug>.md
            └── 02-<slug>.md
```

- `<change-slug>` is English, kebab-case and short (for example
  `product-export`).
- The shared workspace (`workspace/`, `LAST_SESSION.md`, `TODO.md`, `changes/`
  and the `.gitignore` entry) is prepared in Phase 0. A plan run only creates
  the `<change-slug>/` folder.
- `plan.md` is **always** written and is the **single source of truth for the
  execution order**. For a single task, the task is inline. For a split change,
  `plan.md` lists the tasks in order and links to their files.

**Never overwrite an incomplete plan for different work.** Before writing,
check whether `workspace/changes/<change-slug>/plan.md` (or another change
folder) already exists with open items:

- Same work being replanned: update the existing files in place.
- Different work: **stop and ask.** Do not delete, overwrite or rename the
  existing plan. Present the conflict and let the user decide.

### `plan.md` template

The plan itself is written in **Portuguese**, because the user reads it:

```markdown
# Change: <título curto em português>

- **Slug:** <change-slug>
- **Status:** draft | ready | in-progress | done
- **Criado em:** <AAAA-MM-DD>
- **Resumo:** <uma frase>

## Contexto
<o que motivou, comportamento atual, objetivo, quem usa>

## Escopo
- **Dentro:** ...
- **Fora:** ...

## Decisões e premissas
- <decisão> — <motivo>

## Perguntas abertas
- [ ] <pergunta pendente>
<!-- Escreva "Nenhuma." quando não houver pendências.
     A execução ("apply") só começa com esta lista vazia. -->

## Plano de execução

### Task 1: <título>
- **Arquivos prováveis:** `backend/apps/<app>/...`, `frontend/src/...`
- **Critérios de aceite:**
  - [ ] <condição testável>
- **Verificação:**
  - [ ] `cd backend && pytest`
  - [ ] `cd frontend && npm run build`
  - [ ] <checagem manual, se houver>
- **Escopo:** XS | S | M
- **Depende de:** nenhuma

<!-- Só adicione Task 2, Task 3... quando houver necessidade explícita
     de dividir (ver "Task granularity"). -->

## Checkpoints
- [ ] Após a última task: testes passam, lint limpo, build sem erros

## Riscos
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| <risco> | Alto/Médio/Baixo | <estratégia> |

## Progresso
- <AAAA-MM-DD> — plano criado.
```

### `LAST_SESSION.md` and `TODO.md`

Both files are maintained across runs. Create them in Phase 0 if missing,
otherwise update them in place and never overwrite them wholesale.

`workspace/LAST_SESSION.md` is the handoff between sessions, written in
Portuguese:

```markdown
# Última sessão

- **Data:** <AAAA-MM-DD>
- **Change ativo:** <change-slug | nenhum>
- **Status:** em planejamento | em execução | concluído

## O que foi feito
- <resumo curto>

## Próximo passo
- <a próxima ação concreta>
```

Update it at the end of planning and after each execution. It is the first
file to read on the next `planner` run.

`workspace/TODO.md` is the backlog **between** changes: work that left the
current scope, follow-ups and deferred questions:

```markdown
# TODO

- [ ] <item> — origem: <change-slug>
- [x] <item> (AAAA-MM-DD)
```

Keep it short and actionable. When a plan question becomes future work,
record it here and treat the question as resolved.

### Splitting into `tasks/`

Only when the change was split, create one file per task at
`workspace/changes/<change-slug>/tasks/NN-<slug>.md`, numbered in execution
order. Each file has the same per-task fields used inline: description,
probable files, acceptance criteria, verification, scope and dependencies.
In `plan.md`, replace the inline tasks with an ordered index:

```markdown
## Plano de execução
1. [Task 1 — <título>](tasks/01-<slug>.md)
2. [Task 2 — <título>](tasks/02-<slug>.md)
```

Keep the acceptance criteria and verification inside each task file. Keep
`plan.md` as the ordered index plus the shared sections (context, open
questions, risks, progress).

## The `apply` gate

When the user types exactly **`apply`**:

1. Find the active plan: the change folder the user named, or the only one
   under `workspace/changes/`. If several exist and none was named, ask which.
2. Open `plan.md` and check that **every open question is resolved**: no
   unchecked item under **Perguntas abertas** and no leftover placeholder
   (`<...>`, `TBD`, `TODO`). If anything is unresolved, **do not execute**.
   List the open items and ask the user to resolve them.
3. If the user insists while questions remain open, explain that execution
   requires them resolved, and stop.
4. Only when the plan is clear: set **Status** to `in-progress`, set
   `workspace/LAST_SESSION.md` to `em execução`, and start [Execution](#execution).

## Execution

Execute the plan in the order defined in `plan.md`:

- Prefer the project generators (`make:app`, `make:entity`, `generate:schemas`)
  over hand-written boilerplate. Use `project-codegen` for the details, and
  `database-migrations` for migrations.
- Follow the conventions already in the codebase.
- After each task, run its verification steps, then mark its checkboxes `- [x]`
  in `plan.md` (and in the task file, if split) and append a line to
  **Progresso**.
- Keep the system working between tasks. Stop and ask if reality diverges from
  the plan instead of improvising silently.
- Independent tasks may be delegated to subagents, but never parallelize
  migrations or changes to shared state.
- When all tasks and checkpoints pass, set **Status** to `done`, update
  `workspace/LAST_SESSION.md` (date, change, status, what was done, next step),
  add any new out-of-scope items to `workspace/TODO.md`, and report concisely
  what changed.

## Common rationalizations

| Rationalization | Reality |
|---|---|
| "I'll figure it out as I go" | That is how you get rework. Planning first saves the implementation. |
| "The tasks are obvious" | Write them anyway. Explicit tasks surface hidden dependencies. |
| "I don't need to ask, it's clear" | If the plan has a `<...>` or a guess, the context is not clear. Ask. |
| "Let me just split into 8 tasks" | Over-splitting is noise. One task unless there is an explicit need. |
| "Apply now, resolve questions later" | Executing on unresolved questions produces the wrong feature. Resolve first. |
| "The old plan is stale, I'll replace it" | Open items may be mid-build. Stop and ask before overwriting. |

## Red flags

- Writing product code during planning.
- Inventing a convention instead of discovering it from the project.
- Overwriting `LAST_SESSION.md` or `TODO.md` instead of updating them.
- Executing `apply` while **Perguntas abertas** still has items.
- Overwriting a plan with open items for different work without asking.
- A plan without acceptance criteria or verification steps.
- Multiple tasks created without an explicit reason.
- A `plan.md` that does not state the execution order.

## Verification before `apply`

- [ ] Every open question resolved (no unchecked items, no placeholders).
- [ ] Every task has acceptance criteria and a verification step.
- [ ] The execution order in `plan.md` respects the dependencies.
- [ ] The plan lives in `workspace/changes/<change-slug>/plan.md`.
- [ ] No pre-existing incomplete plan was overwritten without asking.
- [ ] `workspace/` is ignored by `.gitignore`.
- [ ] `workspace/LAST_SESSION.md` and `workspace/TODO.md` exist.
- [ ] Conventions were discovered from the project, not invented.
- [ ] No existing workspace file was overwritten.
- [ ] Tasks are Small or Medium (no XL).
- [ ] The user has reviewed the plan.
