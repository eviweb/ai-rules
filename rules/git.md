# Git Workflow

## Permanent branches

| Branch | Role |
|---|---|
| `main` | Stable, always-deployable code. Protected — no direct commits. |
| `develop` | Continuous integration of features before release (optional — use only for projects with a long release cycle). |

For simple projects: `main` alone is sufficient, without `develop`.

## Working branches (short-lived)

Created from `main` (or `develop` if present), deleted after merge.

| Prefix | Usage | Example |
|---|---|---|
| `feat/` | New feature | `feat/add-auth` |
| `fix/` | Bug fix | `fix/login-crash` |
| `chore/` | Maintenance, tooling, dependencies | `chore/update-deps` |
| `docs/` | Documentation only | `docs/api-reference` |
| `test/` | Tests only | `test/add-bats-suite` |
| `release/` | Release preparation (version bump, changelog) | `release/1.2.0` |
| `hotfix/` | Urgent fix applied directly on top of `main` | `hotfix/critical-null-ptr` |

## Synchronization strategy: rebase

When `main` has moved ahead of a working branch, synchronize with:

```bash
git rebase main
```

- Produces a linear, readable history
- Resolves conflicts commit by commit
- **Never rebase a branch that has already been pushed and shared** — this rewrites history and will break other contributors. Use `git push --force-with-lease` only when the branch is personal and you are certain no one else is working on it.

## Merge strategy: squash merge

When merging a PR into `main`, use squash merge:

- One commit per feature/fix on `main` — clean, bisect-friendly history
- Eliminates noise commits (`wip`, `fix typo`, `try again`)
- Rollback is simple: one commit to revert
- **The squash commit message must be written carefully** — do not use the auto-generated message. Write a proper conventional commit message that summarizes the intent of the entire branch.

Exception: hotfixes that consist of a single meaningful commit can be merged directly without squashing.

## Workflow by case

**Feature / fix / chore**
1. Create branch from `main`: `git checkout -b feat/<description>`
2. Develop with conventional commits
3. Rebase on `main` if it has diverged: `git rebase main`
4. Open a PR toward `main`
5. CI green + review → squash merge with a clean commit message
6. Delete the branch

**Hotfix (critical production bug)**
1. Create `hotfix/<description>` from `main`
2. Fix and test
3. Open a PR toward `main` — fast merge
4. Delete the branch

**Release**
1. Create `release/X.Y.Z` from `main`
2. Bump `VERSION`, update `CHANGELOG.md`
3. Open a PR toward `main` → merge → tag `X.Y.Z`
4. Delete the branch

## General rules

- One branch = one topic = one PR
- Keep branches short-lived — rebase regularly to avoid large divergence
- Never merge directly to `main` without a PR
- Branch names must be self-explanatory without additional context

## Deleting merged branches

After a PR is merged on GitHub, always use `git branch -D` (force delete) rather than `git branch -d`:

```bash
# Confirm the PR is merged first
gh pr view <number> --json state -q .state

# Then force-delete the local branch
git branch -D <branch>
```

`git branch -d` checks that the branch SHA exists in the current HEAD history.
When GitHub uses squash merge or rebase merge, commit SHAs are rewritten — the
local branch will never be recognized as merged, and `-d` will always fail.

## Merge conflicts

- Always analyze both sides of a conflict before resolving — never blindly apply `--ours` or `--theirs`
- Prefer manual resolution that preserves the intent of both changes when possible
- If the correct resolution is ambiguous, stop and ask the user before proceeding
