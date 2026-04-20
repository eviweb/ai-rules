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
- [ ] Add `agents/gemini/GEMINI.md` flat entry point
- [ ] Register Gemini agent in `agents.toml` (`install_dir = ~/.gemini`)
- [ ] Add tests for Gemini agent registration and flat file generation
- [ ] Verify `gemini memory list` picks up the symlinked file (trusted folder may be required)

### Rules coverage
- [ ] Add naming conventions for Python, JavaScript/TypeScript, Go in `rules/naming.md`
- [ ] Add `rules/logging.md` for non-CLI projects (log levels, structured logging, aggregation)

## Phase 3 — CI/CD & release
### CI
- [ ] Define caching strategies per ecosystem (npm, pip, cargo…)
- [ ] Define artifact retention policies
- [ ] Define job timeout limits

---

## Future / Postponed
- [ ] Open source documentation (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, issue/PR templates) — validate each with user before creating

## Deferred / Under Consideration
- [ ] Support for additional AI assistants beyond Claude, Codex, Gemini
- [ ] Web UI or TUI for managing agent installations
