# CI Triggers Template (experimental)

> **Status: experimental — not yet part of the mandatory `rules/ci.md` checklist.**
> Validated once on a real project (see below). Apply manually on other
> projects to test before folding it into `ci.md` as a standing requirement.

Complements `rules/ci.md`'s "Triggers" section, which only says *"Run on
`push` and `pull_request`. Add `workflow_dispatch:`."* — true, but a bare
`push:`/`pull_request:` with no filters triggers on **every** ref push
(including tags), **every** PR regardless of target branch, and **every**
file change regardless of content. This template scopes all three.

## Scope decisions this template assumes

- **Branching model: GitHub Flow (direct-to-main)**, not GitFlow. Working
  branches (`feat/`, `fix/`, `chore/`, `docs/`, `test/`, `release/`,
  `hotfix/` — see `rules/git.md`) merge straight into `main`. `develop` is
  kept in the trigger list for projects that opt into the optional
  long-release-cycle model from `rules/git.md`, but is not required — for
  most projects (small team or solo, frequent releases), a two-tier
  develop/main model adds process overhead without a proportional benefit:
  it defers integration feedback to the final merge instead of validating
  every change against the true baseline immediately.
- **Tags never trigger CI.** A tag should only ever be created pointing at
  a commit already validated by `push`/`pull_request` CI on `main` (see
  `rules/release.md`). Re-running CI on the tag itself is redundant. This
  falls out for free from using a `branches:` filter instead of a bare
  `push:` — tag refs never match a `branches:` list.
- **Docs-only changes still run the workflow, but skip the expensive
  jobs.** Two ways to make CI ignore doc-only commits exist —
  trigger-level `paths-ignore:` and the commit-message flag `[skip ci]` —
  and **both share the same trap**: if the workflow never runs at all,
  and "CI" is configured as a *required status check* on branch
  protection, the PR is stuck forever waiting for a check that will never
  report. The fix is to keep the workflow always triggering, and skip
  individual jobs via a job-level `if:` instead — GitHub treats a job
  skipped by `if:` as satisfying a required check, unlike a workflow that
  never ran.

## Template

Adapt the branch prefix list to the project's actual `rules/git.md`
conventions if it deviates, and the `docs-only` file-pattern regex to the
project's actual documentation layout.

```yaml
on:
  push:
    branches:
      - main
      - develop
      - 'feat/**'
      - 'fix/**'
      - 'chore/**'
      - 'docs/**'
      - 'test/**'
      - 'release/**'
      - 'hotfix/**'
  pull_request:
    branches:
      - main
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  detect-changes:
    name: Detect Changes
    runs-on: ubuntu-latest
    timeout-minutes: 5
    outputs:
      docs-only: ${{ steps.check.outputs.docs-only }}
    steps:
      - uses: actions/checkout@<PINNED_SHA> # vX.Y.Z
        with:
          persist-credentials: false
          fetch-depth: 0

      - name: Determine if only docs/text files changed
        id: check
        run: |
          set -euo pipefail
          if [ "${GITHUB_EVENT_NAME}" = "pull_request" ]; then
            range="${{ github.event.pull_request.base.sha }}...${{ github.event.pull_request.head.sha }}"
          else
            before="${{ github.event.before }}"
            if [ -z "${before}" ] || [ "${before}" = "0000000000000000000000000000000000000000" ]; then
              # New branch or force-push with no known prior state — run everything.
              echo "docs-only=false" >> "${GITHUB_OUTPUT}"
              exit 0
            fi
            range="${before}..${{ github.sha }}"
          fi

          changed="$(git diff --name-only "${range}")"
          if [ -z "${changed}" ]; then
            echo "docs-only=false" >> "${GITHUB_OUTPUT}"
          elif printf '%s\n' "${changed}" | grep -qvE '\.md$|^docs/|^\.editorconfig$'; then
            echo "docs-only=false" >> "${GITHUB_OUTPUT}"
          else
            echo "docs-only=true" >> "${GITHUB_OUTPUT}"
          fi

  lint:
    name: Lint
    needs: detect-changes
    if: needs.detect-changes.outputs.docs-only != 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@<PINNED_SHA> # vX.Y.Z
        with:
          persist-credentials: false
      # ... lint steps ...

  test:
    name: Test
    needs: detect-changes
    if: needs.detect-changes.outputs.docs-only != 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@<PINNED_SHA> # vX.Y.Z
        with:
          persist-credentials: false
      # ... test steps ...
```

## Notes

- `fetch-depth: 0` on the `detect-changes` checkout is required — the diff
  range must resolve against real history, and the default shallow
  checkout (`depth: 1`) only has the current commit.
- The `docs-only` regex intentionally excludes workflow files themselves
  (`.github/workflows/*.yml`) — a CI change must always run full CI to
  catch workflow bugs. Extend the regex per project (e.g. add
  `^LICENSE`, `^\.gitignore$`) but never add `\.ya?ml$` or the project's
  own source-file extensions.
- No third-party action is used for the diff — plain `git diff
  --name-only` keeps the action supply chain minimal (see `rules/ci.md`
  § Action supply chain). A project already using `dorny/paths-filter`
  or similar for other reasons may prefer to reuse it instead.
- `pull_request.branches` filters by the PR's *base* (target) branch —
  there is no way to filter by the PR's source branch name via triggers;
  branch-name discipline for sources is enforced by convention
  (`rules/git.md`), not by this filter.

## Validated on

- `neovim-config` (private, personal project) — 2026-09-10. Confirmed via
  a live push that `detect-changes` correctly classifies a docs-only
  commit as `docs-only=true` and a mixed code+docs commit as `false`, and
  that tag pushes no longer trigger a run.
