# Contributing to Praetor

Thanks for your interest in improving Praetor! This document describes the
**branching model (Gitflow)**, the **commit convention** and the **release
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
> receives code through `release/*` and `hotfix/*` branches.

### Supporting branches

| Branch               | Created from | Merged into                    | Naming                    | Purpose                          |
| -------------------- | ------------ | ------------------------------ | ------------------------- | -------------------------------- |
| Feature              | `develop`    | `develop` (PR, `--no-ff`)      | `feature/<short-name>`    | New feature or non-urgent change |
| Bugfix *(optional)*  | `develop`    | `develop` (PR, `--no-ff`)      | `bugfix/<short-name>`     | Non-urgent fix                   |
| Release              | `develop`    | `master` **and** `develop`     | `release/<X.Y.Z>`         | Stabilize a release              |
| Hotfix               | `master`     | `master` **and** `develop`     | `hotfix/<X.Y.Z>`          | Urgent production fix            |

### Rules

- **Never push directly to `master` or `develop`.** Always open a Pull Request.
- Feature and hotfix merges use `--no-ff` to preserve the branch topology.
- A `release/*` or `hotfix/*` branch is **tagged on `master`** as `vX.Y.Z`
  (Semantic Versioning).
- Delete the supporting branch after it is merged.
- Keep branches short-lived: rebase onto the target branch before opening the PR
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

## Pull requests

1. Branch off `develop` (or `master`, for `release/*`/`hotfix/*`).
2. Make sure the full CI is green before requesting review.
3. Open the PR **against `develop`** (or `master` for release/hotfix).
4. Reference the related issue and keep the PR focused on one concern.

### CI gates

The workflow `.github/workflows/ci.yml` must pass. It has three jobs:

| Job        | What it runs                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `backend`  | `ruff check . ../tools` and `pytest`, from `backend/` (Python 3.12, with Redis)                  |
| `frontend` | `npm ci`, `npm run lint`, `npm run build`, from `frontend/`                                      |
| `codegen`  | `make:app sample` + `make:entity product` (from `backend/`), then lint/test the generated app and `npm run build` in `frontend/` |

---

## Release process

1. Branch `release/<X.Y.Z>` from `develop`.
2. Bump the version and update the changelog. Only bug fixes and release
   chores are allowed on this branch.
3. Open a PR into `master` and merge it.
4. Tag the merge commit on `master`:

   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin vX.Y.Z
   ```

5. Merge `master` back into `develop` (so the release commit and tag are
   reachable from `develop`).
6. Delete the `release/<X.Y.Z>` branch.

## Hotfix process

1. Branch `hotfix/<X.Y.Z>` from `master` (increment the **patch** version).
2. Fix the issue and add a regression test.
3. Open a PR into `master`, merge it and tag `vX.Y.Z`.
4. Merge `master` back into `develop`.
5. Delete the `hotfix/<X.Y.Z>` branch.

---

## Bootstrap (first-time setup)

The long-lived `develop` branch already exists (locally and on the remote). When
bootstrapping a fresh fork, create it once from `master`:

```bash
git branch develop master
git push -u origin develop
```

Then, in GitHub → **Settings → Branches**, protect both `master` and `develop`:

- Require a pull request before merging.
- Require the CI status checks (`backend`, `frontend`, `codegen`) to pass.

*Praetor — Building scalable systems, faster.*
