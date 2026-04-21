# TODO

## Phase 1 — Core infrastructure
### CLI
- [x] Bootstrap Python CLI (`install`, `update`, `status`, `list`)
- [x] Add `generate` command for agents without native import support
- [x] Add `remove` command with full state restoration (symlinks + config patches)
- [x] Add `bin/ai-rules-wrapper`: symlink-safe bash entry point
- [x] Shell completion (bash/zsh/fish) via typer
- [x] End-to-end CLI tests (typer `CliRunner` — 24 tests covering all commands with real 3-agent fixture)

### Agent support
- [x] Claude Code integration (`agents/claude/CLAUDE.md`, native imports)
- [x] Codex integration (`agents/codex/AGENTS.md`, flat file + `config_patches` for `project_doc_max_bytes`)
- [x] Register agents in `agents.toml`

### Automation
- [x] `scripts/pre-commit`: regenerate flat files when `rules/` changes
- [x] Update `scripts/pre-commit`: Gemini now uses native imports — skip flat file regeneration for `supports_imports = true` agents; extend trigger to `agents/claude/CLAUDE.md` changes
- [x] `scripts/extract-changelog.sh`: robust CHANGELOG parsing

### Tests
- [x] 58 tests covering agent loading, config resolution, installer, generator, remove

## Phase 2 — Agent coverage
### Gemini integration
Gemini CLI — global config: `~/.gemini/GEMINI.md` (native `@./path` imports, 1M token context)
- [x] Add `agents/gemini/GEMINI.md` as native import file (mirrors `agents/claude/CLAUDE.md`)
- [x] Register Gemini agent in `agents.toml` (`install_dir = ~/.gemini`, `supports_imports = true`)
- [x] Deploy `rules/` symlink alongside `GEMINI.md` in `~/.gemini/`
- [x] Verify Gemini loads all 25 rule files across 17 themes — confirmed

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
- [x] `rules/quality.md`: 11 project quality dimensions (robustness, security, performance, extensibility, user-friendliness, maintainability, observability, testability, portability, auditability, privacy, resilience)
- [x] `rules/error-handling.md`: exit codes, error message format, propagation patterns (shell, Python, Go, JS/TS)
- [x] `rules/api.md`: REST conventions — versioning, HTTP status codes, error response format, pagination, authentication patterns
- [x] `rules/testing.md`: test pyramid, coverage thresholds, test naming conventions, fixture patterns, test data management

### Agent coverage
- [ ] Cursor integration (`agents/cursor/` — `.cursor/rules/*.mdc`, flat file per rule or single file)
- [ ] GitHub Copilot integration (`agents/copilot/` — `.github/copilot-instructions.md`, flat file)
- [ ] Windsurf integration (`agents/windsurf/` — `.windsurfrules`, flat file)
- [ ] Cline / Continue.dev / Aider — investigate config format before committing

### Medium value
- [ ] `rules/docker.md`: Dockerfile best practices, multi-stage builds, .dockerignore, compose conventions, image naming
- [ ] `rules/database.md`: migration conventions, table/column naming, indexing rules, query patterns
- [ ] `rules/python.md`: type hints, dataclasses, async patterns, packaging (beyond naming conventions)
- [ ] `rules/frontend.md`: React/Vue conventions, state management, component structure, bundling

### Lower priority
- [ ] `rules/monitoring.md`: metrics, alerting, observability patterns for services

---

## Future / Postponed
- [ ] Open source documentation (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, issue/PR templates) — validate each with user before creating

## Deferred / Under Consideration
- [ ] Web UI or TUI for managing agent installations
- [ ] Embed rules version header in generated flat files (traceability)
- [ ] `rules/performance.md`: profiling approach, benchmarking conventions, performance budgets
- [ ] `rules/accessibility.md`: a11y standards, ARIA, color contrast — frontend-specific
