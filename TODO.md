# TODO

## Phase 1 — Core infrastructure
### CLI
- [x] Bootstrap Python CLI (`install`, `update`, `status`, `list`)
- [x] Add `generate` command for agents without native import support
- [x] Add `remove` command with full state restoration (symlinks + config patches)
- [x] Add `bin/ai-rules-wrapper`: symlink-safe bash entry point
- [x] Shell completion (bash/zsh/fish) via typer
- [x] End-to-end CLI tests (typer `CliRunner` — 104 tests covering all commands with real 3-agent fixture)
- [x] Global CLI options: `--verbose`, `--quiet`, `--debug`, `--no-color`, `--no-log`, `--log-dir` + file logging to XDG state dir

### Agent support
- [x] Claude Code integration (`agents/claude/CLAUDE.md`, native imports)
- [x] Codex integration (`agents/codex/AGENTS.md`, flat file + `config_patches` for `project_doc_max_bytes`)
- [x] Gemini integration (`agents/gemini/GEMINI.md`, native `@./path` imports, 1M token context)
- [x] Register agents in `agents.toml`

### Automation
- [x] `scripts/pre-commit`: regenerate flat files when `rules/` or `agents/claude/CLAUDE.md` changes
- [x] `scripts/extract-changelog.sh`: robust CHANGELOG parsing

### Tests
- [x] 82 tests covering agent loading, config resolution, installer, generator, remove, CLI commands

## Pre-release fixes
### XDG compliance
- [x] Move backups to `XDG_STATE_HOME/ai-rules/backups/<agent>/` instead of agent install dirs (`~/.claude/backup-*/`, `~/.codex/config.toml.*.bak`)
- [x] `update` command: migrate existing backups from legacy location to XDG path before installing

### Documentation
- [x] README: fix Gemini row (flat file → native imports), add `remove` command to usage, update `rules/` structure (20 → 25 files), update test count
- [x] CHANGELOG: document all unreleased changes from current session

### CI
- [x] Add `scripts/pre-commit` to shellcheck job (no `.sh` extension — currently skipped by `scripts/*.sh` glob)
- [x] Enforce coverage threshold in CI workflow (`--cov-fail-under=80` in pyproject.toml, picked up by CI automatically — 94% current)

### CLI
- [x] `verify` command: check that flat files are in sync with current rules — exits 1 if `generate` would produce a diff (CI use case, catches forgotten `ai-rules generate`)
- [x] Clarify `update` vs `install`: `update` now also runs `generate` for flat-file agents — single command after `git pull`

## Phase 2 — Agent coverage
### Rules coverage
- [x] Add naming conventions for Python, JavaScript/TypeScript, Go in `rules/naming.md`
- [x] Add `rules/logging.md` for non-CLI projects (log levels, structured logging, aggregation)

## Phase 3 — CI/CD & release
### CI
- [x] Define caching strategies per ecosystem (npm, pip, cargo…)
- [x] Define artifact retention policies
- [x] Define job timeout limits

## Phase 4 — Rules expansion
### High value
- [x] `rules/quality.md`: 11 project quality dimensions
- [x] `rules/error-handling.md`: exit codes, error message format, per-language patterns
- [x] `rules/api.md`: REST conventions
- [x] `rules/testing.md`: test pyramid, coverage, naming, fixture patterns

---

## Future / Postponed
- [ ] Bash installer from GitHub: `curl | bash` one-liner with checksum verification, HTTPS, version pinning — secure installation without cloning the repo
- [ ] Agent coverage: Cursor (`.cursor/rules/*.mdc`), GitHub Copilot (`.github/copilot-instructions.md`), Windsurf (`.windsurfrules`)
- [ ] Agent coverage: Cline / Continue.dev / Aider — investigate config format first
- [ ] `rules/docker.md`: Dockerfile best practices, multi-stage builds, compose conventions
- [ ] `rules/database.md`: migration conventions, naming, indexing, query patterns
- [ ] `rules/python.md`: type hints, dataclasses, async, packaging
- [ ] `rules/frontend.md`: React/Vue conventions, state management, component structure
- [ ] `rules/monitoring.md`: metrics, alerting, observability patterns for services

## Deferred / Under Consideration
- [ ] Web UI or TUI for managing agent installations
- [ ] Embed rules version header in generated flat files (traceability)
- [ ] `rules/performance.md`: profiling, benchmarking, performance budgets
- [ ] `rules/accessibility.md`: a11y standards, ARIA, color contrast
- [ ] Versioning: `__version__` in `__init__.py` and `VERSION` file are two
  sources of truth — migrate to `importlib.metadata` reading from `VERSION`
  via hatchling; non-trivial given build toolchain constraints
