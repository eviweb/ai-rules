# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

### Changed
- `.github/workflows/ci.yml`: hardened per `rules/ci.md` guidance — added
  `workflow_dispatch`, workflow-level `permissions: contents: read`,
  `concurrency` with `cancel-in-progress`, `persist-credentials: false` on
  both `actions/checkout` steps (neither job pushes back), and pinned
  `actions/checkout`, `astral-sh/setup-uv`, `actions/cache` to full commit
  SHAs with a trailing version comment (kept on the major version lines
  already in use — v4.x for checkout/cache, v5.x for setup-uv — rather than
  bundling unrelated major bumps into this hardening pass)

### Fixed

## [0.4.0] - 2026-04-21

### Added
- `rules/compatibility.md`: XDG section clarified — scope condition added
  ("applies to any project that writes files to the user's machine; pure
  libraries are exempt"), test isolation rule added, Python code example
  alongside the existing bash one
- Global CLI options: `--verbose`/`-v`, `--quiet`/`-q`, `--debug`, `--no-color`
  (respects `NO_COLOR` env var), `--no-log`, `--log-dir <path>`; file logging
  enabled by default to `XDG_STATE_HOME/ai-rules/logs/ai-rules-YYYY-MM-DD.log`
- XDG Base Directory compliance for backups: link backups and TOML `.bak`
  files now stored under `XDG_STATE_HOME/ai-rules/backups/<agent>/` instead
  of the agent install dir (`~/.claude/backup-*/`, `~/.codex/*.bak`)
- `src/ai_rules/installer.py`: `_xdg_backup_dir()`, `migrate_agent_backups()`
  (moves legacy backups from install dir to XDG state dir, supports `--dry-run`)
- `ai-rules update`: runs `migrate_agent_backups` before install for each agent,
  making it the canonical migration path when upgrading from older versions
- `tests/conftest.py`: autouse fixture redirecting `XDG_STATE_HOME` to a temp
  dir for all tests — prevents writes to `~/.local/state` during the test suite
- `rules/docs.md`: "Keep docs in sync with the code" section — explicit rule
  that doc updates must be in the same commit as the code change, with a table
  mapping change types to affected documents; no more deferred doc passes
- `rules/review.md`: `TODO.md` added to self-review documentation checklist
- `rules/quality.md`: 11 project quality dimensions — robustness, security,
  performance, extensibility, user-friendliness, maintainability, observability,
  testability, portability, auditability, privacy/data minimisation, resilience —
  each with definition, concrete implications, and red flags
- `rules/testing.md`: test pyramid, AAA pattern, naming conventions
  (`test_<unit>_<scenario>_<outcome>`), 80% coverage floor, fixture rules,
  per-language guidance (pytest, bats-core, Jest/Vitest, Go table-driven tests)
- `rules/api.md`: REST API conventions — URL structure, HTTP methods, status codes,
  versioning, JSON envelope, error response format, cursor/offset pagination,
  auth (Bearer), rate limiting with Retry-After, OpenAPI requirement
- `rules/error-handling.md`: exit code table, error message format, per-language
  guidance (shell, Python, Go, JS/TS) — wrapping, re-raising with context, typed errors
- `rules/ci.md`: job timeouts, caching strategies (uv, npm, pnpm, cargo),
  artifact retention policies
- `rules/naming.md`: naming conventions for Python, JavaScript/TypeScript, and Go
- `rules/logging.md`: application-level logging — log levels, structured JSON
  format, XDG log path, aggregation strategies, per-language guidance
- `rules/commits.md`: prefer detailed commit messages
- `rules/cli.md`: require shell completion for every CLI tool
- Gemini integration: native `@./path` imports, 1M token context — `GEMINI.md`
  rewritten as an import file mirroring `CLAUDE.md`; `rules/` symlinked into
  `~/.gemini/`; `supports_imports = true` in `agents.toml`
- Codex: `config_patches` mechanism — installer patches `~/.codex/config.toml`
  in-place (`project_doc_max_bytes = 131072`) with backup, preserving existing
  user configuration; no symlink to a repo-tracked config file
- `ai-rules remove` command: unlinks symlinks managed by ai-rules and restores
  the most recent backup; reverts config patches (restore `.bak` or remove key)
- `ai-rules verify` command: checks flat files are in sync with current rules,
  exits 1 if any are missing or stale — intended for CI use
- `ai-rules update` now combines install + generate: redeploys symlinks and
  regenerates flat files for flat-file agents in one step
- `src/ai_rules/generator.py`: `condense_content()` strips fenced code blocks
  and collapses blank lines; `verify_flat_file()` compares output against
  resolved source; `condense` kwarg on `generate_flat_file()`
- `src/ai_rules/installer.py`: `ConfigPatch` dataclass, `_patch_toml_file()`,
  `_unpatch_toml_file()`, `remove_agent()`, backup/restore helpers
- `src/ai_rules/agent.py`: `ConfigPatch` dataclass, `condense_flat_file` field
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`,
  `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`,
  `.github/PULL_REQUEST_TEMPLATE.md`, `AUTHORS.md`
- `bin/ai-rules-wrapper`: symlink-safe bash entry point
- Codex integration: `agents/codex/AGENTS.md` flat file, `ai-rules generate`
  command, `resolve_imports()` and `generate_flat_file()` in `generator.py`

### Changed
- `.github/workflows/ci.yml`: add `ai-rules verify` step to test job
  (catches forgotten `ai-rules generate` in CI); add job timeouts (lint: 5 min,
  test: 15 min); add uv dependency cache keyed on `uv.lock`
- `scripts/pre-commit`: also triggers on `agents/claude/CLAUDE.md` changes
  (source for Codex flat file generation); Gemini flat file regeneration
  dropped (now uses native imports)
- `ai-rules update`: previously identical to `install`; now also regenerates
  flat files for agents with `supports_imports = false`

### Fixed
- `tests/test_gemini.py`: remove unused `resolve_imports` import (ruff F401)
- CI: `scripts/pre-commit` added to shellcheck step (no `.sh` extension —
  previously excluded by `scripts/*.sh` glob)
- CI: coverage threshold enforced via `--cov-fail-under=80` in pytest config
  (current coverage: 94%)
- CLI e2e test fixture: changed from symlinks to copies of `rules/` and
  `agents/` to prevent tests from modifying real repo files

## [0.3.1] - 2026-03-26

### Added
- `.github/workflows/ci.yml`: CI pipeline with lint (shellcheck + ruff) and
  test (pytest on Python 3.11 and 3.12) jobs, triggered on push and PR
- `ruff>=0.4.0` added to dev dependencies
- CI badge added to `README.md`

### Fixed
- CI workflow: replace `uv pip install --system` with `uv sync` + `uv run`
  to comply with PEP 668 (externally managed Python on Debian/Ubuntu runners)
- Unused imports removed in `tests/test_agent.py` (ruff F401)
- `rules/git.md`: document `git branch -D` requirement after GitHub squash/rebase merge
- `README.md`: fix dev installation command (`uv pip install` → `uv sync --extra dev`)

## [0.3.0] - 2026-03-26

### Added
- Python CLI (`ai-rules`) with `install`, `update`, `status`, and `list` commands
- `src/ai_rules/` package: `agent.py`, `config.py`, `installer.py`, `cli.py`
- `pyproject.toml`: hatchling build backend, typer, pytest dev dependencies
- `bin/ai-rules`: development entry point (no installation required)
- `agents.toml`: agent registry with link declarations (Claude Code)
- `agents/claude/CLAUDE.md`: Claude Code entry point (moved from repo root)
- 20 tests covering agent loading, repo root resolution, and install logic
- `tests/run-tests.sh`: test runner wrapper
- Shell completion support via `ai-rules --install-completion` (bash/zsh/fish)

### Changed
- Repository renamed from `claude-config` to `ai-rules`
- `CLAUDE.md` moved to `agents/claude/CLAUDE.md`
- `README.md` rewritten to reflect new scope and CLI usage
- `.gitignore` extended with Python artifact patterns

### Removed
- `install.sh` replaced by the `ai-rules install` CLI command

## [0.2.0] - 2026-03-26

### Added
- `rules/principles.md`: general coding principles (analyze before coding,
  propose before implementing, propose options before deciding, clarify before
  starting, prefer minimal diffs, no refactoring without request, no speculative
  additions, no dead code, confirm before irreversible actions, explicit naming)
- `scripts/extract-changelog.sh`: extract release notes for a given version
  from CHANGELOG.md — robust against semver metadata and end-of-file edge cases
- `TODO.md`: deferred items tracker (naming conventions, CI advanced topics,
  logging, open source documentation)
- `settings.json` versioned in the repository with global Claude Code permissions
- `install.sh` now deploys a symlink for `settings.json` into `~/.claude/`

### Changed
- `rules/git.md`: full branch workflow (permanent and short-lived branches,
  rebase strategy, squash merge, workflows by case, merge conflict guidelines)
- `rules/cli.md`: add structured invocation format (namespace/command/subcommand)
- `rules/commits.md`: clarify commit message must cover all modified files
- `rules/security.md`: add `.env.example` pattern
- `rules/review.md`: restructure as full review guidelines with self-review
  checklist and code review sections (solo vs team projects)
- `rules/release.md`: detail platform release workflow for GitHub and Forgejo,
  replace inline sed with `scripts/extract-changelog.sh`
- `CLAUDE.md`: add `rules/principles.md` reference under new section

### Fixed
- README structure now lists all 20 rule files including `principles.md`

## [0.1.0] - 2026-03-24

### Added
- 20 global rule files covering language, naming, editor, general principles,
  TDD, security, dependencies, compatibility, documentation, changelog,
  versioning, shell, CLI, git, commits, issues, PR, review, CI/CD, and release
- `install.sh` to deploy symlinks into `~/.claude/`
