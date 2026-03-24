# Continuous Integration

## Setup
- Workflow files:
  - Forgejo: `.forgejo/workflows/`
  - GitHub: `.github/workflows/`
- Propose the CI structure at project start and wait for user validation before creating it
- Add a CI status badge to `README.md` once the workflow is in place

## Triggers
- Run on `push` and `pull_request`

## Jobs
- **lint** — run `shellcheck` on all shell scripts
- **test** — run the bats-core test suite
- **build** — run if the project produces build artifacts

## Rules
- Fail fast on error
- Never hardcode secrets in workflow files — use platform secrets (Forgejo variables/secrets or GitHub Actions secrets)
