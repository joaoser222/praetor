---
name: publish-workflow
description: >
  RESTRICTED USE: activate ONLY when the user types exactly "publish" or
  exactly "publish_production". DO NOT activate for "publish it", "publicar",
  "release", "merge", "deploy", "tag" or any other variation. "publish" merges
  the current feature/bugfix branch into develop locally with --no-ff and
  pushes develop. "publish_production" merges develop into master locally with
  --no-ff, tags vX.Y.Z, pushes master and the tag, then merges master back into
  develop and pushes it. No Pull Requests and no CI wait.
compatibility:
  - git
---

# Publish Workflow — Praetor

## When to use

Activate this skill **exclusively** when the user types one of these exact
words in the chat:

- `publish` — merges the current feature/bugfix branch into `develop`.
- `publish_production` — merges `develop` into `master` as a release.

Any other wording does not activate the skill. The rules of the branching
model are in `CONTRIBUTING.md`; this skill is the procedure.

## Hard rules

- **No Pull Requests and no CI wait.** Merges are local, and the push is the
  publication.
- **Never force-push, never rewrite history, never move or delete a tag.**
- **Use `--no-ff`** so every merge keeps its merge commit.
- **Stop on any error.** On a merge conflict, run `git merge --abort`, report
  the conflicting files, and stop.
- Communicate with the user in **Portuguese (pt-BR)**. Command names, branch
  names and tags stay in English.

## Preconditions (check before any step)

1. Working tree clean: `git status --short` prints nothing. If not, stop and
   offer to commit with the `commit` skill first.
2. For `publish`: the current branch matches `feature/<name>` or
   `bugfix/<name>`. Refuse on `master`, `develop`, `release/*` and `hotfix/*`.
3. For `publish_production`: the version `X.Y.Z` must come from the user; do
   not guess it. The tag `vX.Y.Z` must not exist yet
   (`git rev-parse -q --verify refs/tags/vX.Y.Z` prints nothing).
4. If `backend/pyproject.toml` has a version different from `X.Y.Z`, stop and
   ask whether to commit the bump first.

## `publish`: branch → `develop`

1. Bring `develop` up to date:
   ```bash
   git fetch origin
   git switch develop
   git pull --ff-only origin develop
   ```
2. Merge the branch with a merge commit:
   ```bash
   git merge --no-ff <branch> -m "Merge branch '<branch>' into develop"
   ```
3. Publish `develop`:
   ```bash
   git push origin develop
   ```
4. Remove the merged branch, locally and on the remote:
   ```bash
   git branch -d <branch>
   git push origin --delete <branch>
   ```

## `publish_production`: `develop` → `master`

1. Bring `develop` and `master` up to date:
   ```bash
   git fetch origin
   git switch develop
   git pull --ff-only origin develop
   git switch master
   git pull --ff-only origin master
   ```
2. Merge `develop` into `master`:
   ```bash
   git merge --no-ff develop -m "Merge branch 'develop' into master"
   ```
3. Tag the merge commit:
   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   ```
4. Publish `master` and the tag:
   ```bash
   git push origin master
   git push origin vX.Y.Z
   ```
5. Bring `master` back into `develop`, so the release commit and the tag are
   reachable from `develop`, and publish it:
   ```bash
   git switch develop
   git merge --no-ff master -m "Merge branch 'master' into develop"
   git push origin develop
   ```

## Failure handling

- **Merge conflict:** `git merge --abort`, report the files, stop. Resolve it
  in a feature branch, not in `develop` or `master`.
- **`git pull --ff-only` fails:** local and remote diverged. Stop and ask the
  user; do not rewrite history.
- **`git push` rejected:** stop and report. Never use `--force`.
- **Tag already exists:** stop and ask. Never move or delete a published tag.

## Red flags

- Committing directly to `develop` or `master`.
- Pushing before the merge is complete and verified.
- Creating a tag without the user confirming the version.
- Skipping step 5 of `publish_production`.
- Using `--force`, `-D` or `--squash` on these merges.
