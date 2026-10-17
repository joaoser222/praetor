# Contributing to Praetor

Thanks for your interest in improving Praetor! This document describes the
**branching model (Gitflow)**, the **commit convention** and the **publishing
process** used by this repository.

---

## Branching model: Gitflow

Praetor uses the **full Gitflow** model. There are two long-lived branches and
several short-lived supporting branches.

### Long-lived branches

| Branch    | Role                                                                 | Direct commits |
| --------- | -------------------------------------------------------------------- | -------------- |
| `master`  | Production-ready code. Every commit is a released version (tagged).  | ❌ Never       |
| `develop` | Integration branch. Reflects the latest delivered development changes. | ❌ Never      |

> `develop` is the **default target** for day-to-day work. `master` only
> receives code through the release and hotfix flows below.

### Supporting branches

| Branch               | Created from | Merged into                    | Naming                    | Purpose                          |
| -------------------- | ------------ | ------------------------------ | ------------------------- | -------------------------------- |
| Feature              | `develop`    | `develop` (`publish`, `--no-ff`) | `feature/<short-name>`  | New feature or non-urgent change |
| Bugfix *(optional)*  | `develop`    | `develop` (`publish`, `--no-ff`) | `bugfix/<short-name>`   | Non-urgent fix                   |
| Release              | `develop`    | `master` **and** `develop` (`publish_production`) | `release/<X.Y.Z>` | Stabilize a release |
| Hotfix               | `master`     | `master` **and** `develop`     | `hotfix/<X.Y.Z>`          | Urgent production fix            |

### Rules

- **Never commit directly to `master` or `develop`.** Code reaches them only
  through the `publish` and `publish_production` procedures.
- Merges use `--no-ff` to preserve the branch topology.
- A `master` release is **tagged** as `vX.Y.Z` (Semantic Versioning).
- Delete the supporting branch after it is merged.
- Keep branches short-lived: merge `develop` into the branch before publishing
  if it has drifted.

### Naming

Lowercase, hyphen-separated, short and descriptive:

```text
feature/user-profile
bugfix/token-expiry
release/1.3.0
hotfix/1.2.1
```

---

## Commit convention

Commits follow the **Angular Convention** with the **description in Brazilian
Portuguese (pt-BR)** — see `.agents/skills/git-commit/SKILL.md`.

```text
<type>(<scope>): <descrição em português>
```

| Type       | When to use                                    |
| ---------- | ---------------------------------------------- |
| `feat`     | New feature                                    |
| `fix`      | Bug fix                                        |
| `refactor` | Refactor with no behavior change               |
| `chore`    | Infrastructure, CLI, config, build tasks       |
| `docs`     | Documentation                                  |
| `test`     | Tests                                          |
| `style`    | Formatting / linting only                      |

- The **description must be ≤ 72 characters**.
- `scope` is the affected module/domain (e.g. `auth`, `core`, `db`, `codegen`).
- Use the imperative mood and **no trailing period**.

Examples:

```text
feat(auth): grava cookies HttpOnly no login
fix(db): avisa quando não há revisões de migração
chore(ci): adiciona job de codegen
```

---

## Publishing

There are no Pull Requests and no CI gate in this flow. Publishing is a
**local `--no-ff` merge followed by a push**, and it is run with the keywords
below. The step-by-step procedure is in `.agents/skills/publish-workflow/SKILL.md`.

| Keyword              | Effect                                                                 |
| -------------------- | ---------------------------------------------------------------------- |
| `publish`            | Merges the current `feature/*` or `bugfix/*` branch into `develop`, pushes `develop`, and deletes the merged branch. |
| `publish_production` | Merges `develop` into `master`, tags `vX.Y.Z`, pushes `master` and the tag, then merges `master` back into `develop` and pushes it. |

Before publishing, the working tree must be clean. Changes are committed with
the `commit` skill.

---

## CI

`.github/workflows/ci.yml` runs on push and pull request, with three jobs:

| Job        | What it runs                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `backend`  | `ruff check . ../tools` and `pytest`, from `backend/` (Python 3.12, with Redis)                  |
| `frontend` | `npm ci`, `npm run lint`, `npm run build`, from `frontend/`                                      |
| `codegen`  | `make:app sample` + `make:entity product` (from `backend/`), then lint/test the generated app and `npm run build` in `frontend/` |

The CI reports the state of each push. It is **not** a gate of the publish
flow in this repository.

---

## Hotfix

1. Create `hotfix/<X.Y.Z>` from `master` (increment the **patch** version) and
   fix the issue, with a regression test.
2. Merge it into `master` with `--no-ff`, tag `vX.Y.Z`, and push.
3. Merge `master` back into `develop` with `--no-ff` and push.
4. Delete the `hotfix/<X.Y.Z>` branch.

---

## Bootstrap (first-time setup)

The long-lived `develop` branch already exists (locally and on the remote). When
bootstrapping a fresh fork, create it once from `master`:

```bash
git branch develop master
git push -u origin develop
```

*Praetor — Building scalable systems, faster.*
