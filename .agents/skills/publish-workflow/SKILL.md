---
name: publish-workflow
description: >
  RESTRICTED USE: activate ONLY when the user types exactly "publish" or
  exactly "publish_production". DO NOT activate for "publish it", "publicar",
  "release", "merge", "deploy", "tag" or any other variation. "publish"
  opens a Pull Request from the current feature/bugfix branch into develop,
  waits for CI and merges it with --no-ff. "publish_production" opens a
  release PR from develop into master, merges it, tags vX.Y.Z and syncs
  master back into develop through a second PR. Never pushes directly to
  master or develop.
compatibility:
  - git
  - gh (GitHub CLI, authenticated)
---

# Publish Workflow — Praetor

## When to use

Activate this skill **exclusively** when the user types one of these exact
words in the chat:

- `publish` — publishes the current feature/bugfix branch into `develop`.
- `publish_production` — publishes `develop` into `master` as a release.

Any other wording does not activate the skill.

The full rules live in `CONTRIBUTING.md` (Gitflow, branch names, CI gates).
This skill is the operational procedure.

## Hard rules

- **Never push or commit directly to `master` or `develop`.** Every change
  enters through a Pull Request.
- **Use `--merge` (not squash, not rebase)** so the merge commit is kept
  (`--no-ff` semantics), as required by `CONTRIBUTING.md`.
- **Never merge with a red CI.** Wait for the required checks: `backend`,
  `frontend`, `codegen`. If a check fails, stop and report it.
- **Never skip the local sync** after a merge (see the sync steps). GitHub
  does not update the local repository.
- Communicate with the user in **Portuguese (pt-BR)**. Command names,
  branch names and tags stay in English.

## Preconditions (check before any step)

1. Working tree clean: `git status --short` prints nothing. If there are
   pending changes, stop and say so. Offer to commit them first with the
   `commit` skill.
2. `gh` is authenticated: `gh auth status`.
3. For `publish`: the current branch must match `feature/<name>` or
   `bugfix/<name>`. Refuse on `master`, `develop`, `release/*` and
   `hotfix/*`.
4. For `publish_production`: the version `X.Y.Z` must be confirmed with the
   user before anything else (SemVer). Do not guess it.

## `publish`: branch → `develop`

1. Push the branch and set upstream:
   ```bash
   git push -u origin "$(git branch --show-current)"
   ```
2. Open the PR against `develop`:
   ```bash
   gh pr create --base develop --head "$(git branch --show-current)" --fill
   ```
   Note the PR number printed by `gh`.
3. Wait for the CI checks to finish and check they are green:
   ```bash
   gh pr checks <number> --watch
   ```
   If any required check fails, stop and report which one.
4. Merge with a merge commit and delete the remote branch:
   ```bash
   gh pr merge <number> --merge --delete-branch
   ```
5. Sync the local repository and delete the local branch:
   ```bash
   git switch develop
   git pull --ff-only
   git branch -d <branch>
   ```
   If `git branch -d` refuses, the branch was not merged locally. Report it
   instead of forcing with `-D`.

## `publish_production`: `develop` → `master`

1. Sync `develop` first:
   ```bash
   git switch develop
   git pull --ff-only
   ```
2. Create the release branch from `develop`, confirm the version in
   `backend/pyproject.toml`, and push it:
   ```bash
   git switch -c release/X.Y.Z develop
   git push -u origin release/X.Y.Z
   ```
   Only bug fixes and release chores may be added to this branch.
3. Open the PR against `master`:
   ```bash
   gh pr create --base master --head release/X.Y.Z --fill
   ```
4. Wait for the CI checks (`gh pr checks <number> --watch`), then merge:
   ```bash
   gh pr merge <number> --merge --delete-branch
   ```
5. Sync `master` and tag the merge commit:
   ```bash
   git switch master
   git pull --ff-only
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin vX.Y.Z
   ```
6. Bring `master` back into `develop` through a second PR. This keeps the
   release commit and the tag reachable from `develop`. Do not skip it:
   ```bash
   gh pr create --base develop --head master \
     --title "chore(release): sincroniza master em develop" \
     --body "Traz o merge da release vX.Y.Z de volta para develop."
   gh pr checks <number> --watch
   gh pr merge <number> --merge
   ```
   Do not delete `master`.
7. Sync local `develop` and delete the local release branch:
   ```bash
   git switch develop
   git pull --ff-only
   git branch -d release/X.Y.Z
   ```

## Hotfix

A hotfix follows the same shape, with two differences: the branch is
`hotfix/X.Y.Z` created from `master`, and the first PR targets `master`.
Ask the user for the version before starting.

## Failure handling

- **Merge conflict** on a PR: resolve it on the PR branch, never on
  `master` or `develop`. Then re-run the checks.
- **Failed CI**: stop, report the failing job, and do not merge.
- **`git pull --ff-only` fails**: local and remote diverged. Stop and ask
  the user; do not rewrite history.
- **Tag already exists**: stop and ask. Never move or delete a published tag.

## Red flags

- Pushing or committing to `master` or `develop` directly.
- Merging with a red or missing CI check.
- Creating a tag without the user confirming the version.
- Skipping the step that brings `master` back into `develop`.
- Using `-D` (force delete) or `--squash` on these merges.
