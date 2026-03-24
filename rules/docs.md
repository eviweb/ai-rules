# Documentation

Every project must include the following files from the start:

- `README.md` — project description, usage, install instructions
- `CHANGELOG.md` — updated on every meaningful change
- `VERSION` — single line, semver (e.g. `1.0.0`), source of truth for version numbers
- `LICENSE.md` — ask the user to validate the license choice before creating it

Keep all documentation up to date as the project evolves.

## Community / open source (on user request)

When the user intends to share the project publicly, propose the following files and wait for explicit validation before creating each one:

- `CONTRIBUTING.md` — contribution guidelines (workflow, conventions, PR process)
- `CODE_OF_CONDUCT.md` — code of conduct (e.g. Contributor Covenant)
- `SECURITY.md` — vulnerability reporting policy
- `SUPPORT.md` — where to get help
- `.github/ISSUE_TEMPLATE/bug_report.md` — bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` — pull request template
- `AUTHORS.md` — list of contributors (optional, ask user)

The application/script must read its version from the `VERSION` file, not from a hardcoded constant.

**First commit of a new project:** `init: <short message>` with a detail block.
**Subsequent commits:** standard conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, etc.).
