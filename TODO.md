# TODO

Improvements and additions to consider for future iterations of this config.

## Codex integration
- [ ] Add `agents/codex/AGENTS.md` entry point (flat file — no @rules/ import support)
- [ ] Add `generate` command to CLI: concatenate rules/ into a flat file for agents without native import support
- [ ] Register Codex agent in `agents.toml`
- [ ] Add tests for generate command and Codex agent

## Naming conventions
- [ ] Add naming conventions for other languages (JavaScript/TypeScript, Python, Go...) in `rules/naming.md` as they become relevant in projects

## CI/CD
- [ ] Define caching strategies per language/ecosystem (npm, pip, cargo...)
- [ ] Define artifact retention policies
- [ ] Define job timeout limits

## Logging (application-level)
- [ ] Add a `rules/logging.md` for non-CLI projects: log levels, structured logging, log aggregation patterns

## Release
- [x] Extract CHANGELOG parsing logic into a dedicated `scripts/extract-changelog.sh` — the inline `sed` command in `rules/release.md` is fragile (does not handle semver metadata like `1.0.0-rc.1` or end-of-file edge cases)

## Open source / public documentation
If this repository is intended to be shared publicly, add the following files (validate each with user before creating, as per `rules/docs.md`):
- [ ] `LICENSE.md` — validate license choice with user first
- [ ] `CONTRIBUTING.md` — contribution guidelines (workflow, conventions, PR process)
- [ ] `CODE_OF_CONDUCT.md` — e.g. Contributor Covenant
- [ ] `SECURITY.md` — vulnerability reporting policy
- [ ] `SUPPORT.md` — where to get help
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `AUTHORS.md` — optional, ask user
