# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
