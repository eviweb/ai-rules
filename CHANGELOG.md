# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `rules/error-handling.md`: exit code table, error message format, per-language
  guidance (shell, Python, Go, JS/TS) — wrapping, re-raising with context, typed errors
- `rules/ci.md`: add job timeouts (table + yaml example), caching strategies for
  Python/uv, npm, pnpm, Rust/cargo (lockfile-keyed with restore-keys), artifact
  retention policies (7 days ephemeral, 90 days release)
- `rules/naming.md`: add naming conventions for Python, JavaScript/TypeScript, and Go
- Gemini integration: `agents/gemini/GEMINI.md` flat entry point, agent registered
  in `agents.toml` (`install_dir = ~/.gemini`, no import support), 6 tests in
  `tests/test_gemini.py`, symlink deployed to `~/.gemini/GEMINI.md`
- `rules/logging.md`: application-level logging rules — log levels, structured JSON
  format, XDG log path, aggregation strategies, per-language guidance (Python, shell, Node.js)
- `bin/ai-rules-wrapper`: symlink-safe bash entry point — resolves repo root via
  `readlink -f`, sets `AI_RULES_HOME`, and delegates to the venv Python CLI
- `src/ai_rules/cli.py`: add `__main__` block to support `python3 -m ai_rules.cli`
- `TODO.md`: Gemini integration section with discovery strategy and task list
- Codex integration: `agents/codex/AGENTS.md` flat entry point (all rules inlined)
- `ai-rules generate` command: resolves `@rules/` imports and writes a flat file
  for agents without native import support (`supports_imports = false`)
- `src/ai_rules/generator.py`: `resolve_imports()` and `generate_flat_file()` functions
- `agents.toml`: Codex agent registered (`install_dir = ~/.codex`, no import support)
- `tests/test_generator.py`: 7 tests for the generator module
- `rules/cli.md`: require shell completion for every CLI tool
- `rules/commits.md`: prefer detailed commit messages

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
