# Git Workflow

## Project profile

Read this first: it conditions the rules below. Declare the profile in the project `README.md`. If undeclared, apply **strict**.

| | light (solo, small project) | strict (shared, public, or consumed artifact) |
|---|---|---|
| PR | Recommended for `feat/` and `fix/`; direct commit on `main` tolerated for trivial `docs/`, `chore/` and the release commit | Mandatory for everything, release included |
| Safeguard | Pre-commit hook, tests green locally | Platform branch protection: required checks, direct push blocked |

Strict applies if any is true: several contributors, public repo with consumers, branch protection enabled.

Common to both: no force-push on `main`, tests green before tagging, tags only on a commit validated by CI, one topic per branch or commit.

## Branches

- `main`: stable, always-deployable, protected (light profile: see exceptions above). `develop` only for projects with a long release cycle.
- Working branches are short-lived, created from `main`, deleted after merge, one topic each: `feat/`, `fix/`, `chore/`, `docs/`, `test/`, `release/X.Y.Z` (version bump + changelog), `hotfix/` (urgent fix on top of `main`, fast merge). Names must be self-explanatory (`feat/add-auth`).
- Flow: branch from `main`, conventional commits, open a PR toward `main`, CI green + review, merge commit, delete the branch. Never merge directly to `main` without a PR (strict profile).

## Synchronization: rebase

When `main` moved ahead, run `git rebase main`: linear history, conflicts resolved commit by commit. **Never rebase a branch that is pushed and shared.** Use `git push --force-with-lease` only on a personal branch nobody else works on.

## Merge: merge commit

Use `gh pr merge --merge`:

- Original commits keep their author signature (`Verified`); the platform signs the merge commit. Squash replaces the signature and rebase leaves commits `unsigned`: use neither when signatures matter.
- History is non-linear: `git log --first-parent main` gives the per-PR view.
- Commit messages survive as-is: clean the branch before pushing (`git rebase -i`, only while not shared), no `wip` / `fix typo` commits.
- Do not enable "require linear history" (incompatible); "require signed commits" is compatible.

## Deleting merged branches

Run `git branch -d <branch>`; it works because merge commits keep the SHAs reachable. If it fails, the PR was merged another way: confirm with `gh pr view <number> --json state -q .state`, then use `-D`.

## Merge conflicts

- Analyze both sides before resolving; never blindly apply `--ours` or `--theirs`.
- Prefer a manual resolution that preserves the intent of both changes.
- If the correct resolution is ambiguous, stop and ask the user.
