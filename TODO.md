# TODO

## Phase 1 — Core infrastructure
### CLI
- [x] Bootstrap Python CLI (`install`, `update`, `status`, `list`)
- [x] Add `generate` command for agents without native import support
- [x] Add `bin/ai-rules-wrapper`: symlink-safe bash entry point
- [x] Shell completion (bash/zsh/fish) via typer

### Agent support
- [x] Claude Code integration (`agents/claude/CLAUDE.md`, native imports)
- [x] Codex integration (`agents/codex/AGENTS.md`, flat file)
- [x] Register agents in `agents.toml`

### Automation
- [x] `scripts/pre-commit`: regenerate flat files when `rules/` changes
- [x] `scripts/extract-changelog.sh`: robust CHANGELOG parsing

### Tests
- [x] 27 tests covering agent loading, config resolution, installer, generator

## Phase 2 — Agent coverage
### Gemini integration
Gemini CLI v0.36.0 — global config: `~/.gemini/GEMINI.md` (no native imports)
- [x] Add `agents/gemini/GEMINI.md` flat entry point
- [x] Register Gemini agent in `agents.toml` (`install_dir = ~/.gemini`)
- [x] Add tests for Gemini agent registration and flat file generation
- [x] Verify `gemini memory list` picks up the symlinked file — confirmed: file loaded as context, `memory list` only shows `## Gemini Added Memories` entries (expected)

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
- [x] `rules/error-handling.md`: exit codes, error message format, propagation patterns (shell, Python, Go, JS/TS)
- [x] `rules/api.md`: REST conventions — versioning, HTTP status codes, error response format, pagination, authentication patterns
- [ ] `rules/testing.md`: test pyramid, coverage thresholds, test naming conventions, fixture patterns, test data management

### Agent coverage
- [ ] Cursor integration (`agents/cursor/` — `.cursor/rules/*.mdc`, flat file per rule or single file)
- [ ] GitHub Copilot integration (`agents/copilot/` — `.github/copilot-instructions.md`, flat file)

### Medium value
- [ ] `rules/docker.md`: Dockerfile best practices, multi-stage builds, .dockerignore, compose conventions, image naming
- [ ] `rules/database.md`: migration conventions, table/column naming, indexing rules, query patterns

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
