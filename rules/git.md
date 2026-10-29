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

## Merge strategy: merge commit

When merging a PR into `main`, use a merge commit (`gh pr merge --merge`):

- Original commits keep their author GPG signature (`Verified`); the merge commit is signed by the platform
- Squash replaces the signature with the platform's; rebase rewrites commits and leaves them `unsigned` — do not use either when signatures matter
- History is non-linear: `git log --first-parent main` gives the linear, per-PR view
- Commit messages survive as-is on `main`: clean the branch before pushing (`git rebase -i`, only while it is not shared) and write the merge message carefully — no `wip` / `fix typo` commits
- Do not enable "require linear history" in the ruleset (incompatible); "require signed commits" is compatible

## Workflow by case

**Feature / fix / chore**
1. Create branch from `main`: `git checkout -b feat/<description>`
2. Develop with conventional commits
3. Rebase on `main` if it has diverged: `git rebase main`
4. Open a PR toward `main`
5. CI green + review → merge commit with a clean message
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

## Project profile

Declare the profile in the project `README.md`. If undeclared, apply **strict**.

| | light (solo, small project) | strict (shared, public, or consumed artifact) |
|---|---|---|
| PR | Recommended for `feat/` and `fix/`; direct commit on `main` tolerated for trivial `docs/`, `chore/` and the release commit | Mandatory for everything, release included |
| Safeguard | Pre-commit hook, tests green locally | Platform branch protection: required checks, direct push blocked |

Strict applies if any is true: several contributors, public repo with consumers, branch protection enabled.

Common to both: no force-push on `main`, tests green before tagging, tags only on a commit validated by CI, one topic per branch or commit.

## General rules

- One branch = one topic = one PR
- Keep branches short-lived — rebase regularly to avoid large divergence
- Never merge directly to `main` without a PR (strict profile; see Project profile)
- Branch names must be self-explanatory without additional context

## Deleting merged branches

After a PR is merged, delete the local branch:

```bash
git branch -d <branch>
```

`-d` works because merge commits keep the original SHAs reachable from `main`. If it fails, the PR was merged another way (squash/rebase): confirm with `gh pr view <number> --json state -q .state`, then use `-D`.

## Merge conflicts

- Always analyze both sides of a conflict before resolving — never blindly apply `--ours` or `--theirs`
- Prefer manual resolution that preserves the intent of both changes when possible
- If the correct resolution is ambiguous, stop and ask the user before proceeding
