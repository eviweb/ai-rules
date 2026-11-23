# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Skill directory link type (`[[agents.*.skill_dirs]]` in `agents.toml`): `install` / `update` link each skill folder (a folder holding a `SKILL.md`) under the agent's skills directory, one symlink per skill so user-authored skills coexist; `update` unlinks skills removed from the repository, `remove` unlinks only ai-rules skills (restoring backed-up folders), `status` reports each skill. No agent declares one yet
- Skill format and `ai-rules skills list|verify|status` (`src/ai_rules/skills.py`, `docs/skills.md`): strict frontmatter parser without YAML dependency; `verify` checks name = folder name with the `ai-rules-` prefix, description starting with `Use when` (≤ 300 characters), supported fields only, `SKILL.md` ≤ 8 KiB, existing references, executable and shellcheck-clean scripts, and the `derived-from` / `license-of-origin` / `THIRD_PARTY.md` chain for skills derived from another project; the same checks run in the test suite

### Changed
- Roadmap reordered: skills infrastructure and four transition skills (`starting-a-project`, `quality-dimensions`, `reviewing-changes`, `pull-requests-and-issues`) now come first (0.7.0, additive), then core slimming and scoped rules (0.8.0, breaking), so no rule is unloaded before its skill exists; the global compaction pass is replaced by a targeted condensation of the core with an invariants test

### Fixed

## [0.6.3] - 2026-11-19

### Added
- Managed JSON merge for agent settings (`[[agents.*.settings_merge]]` in `agents.toml`, `src/ai_rules/settings_merge.py`): ai-rules writes only the key paths it owns, records additions in `$XDG_STATE_HOME/ai-rules/state/`, and `update` / `remove` retire or revert exactly those entries; `status` reports the merged file

### Changed
- Claude Code permissions: `git commit *`, `git push *`, `rm *`, `npx *` and `chmod *` move from `allow` to `ask` (aligns with the "never commit autonomously" rule); `deny` now also blocks `rm -fr/-r/-R/-Rf/-fR`, forced `git push` (`--force`, `-f`; `--force-with-lease` still asks), `git reset --hard`, `git checkout -- <path>`, `git clean` and `git branch -D`; `update` retires the entries that left `allow`
- **Breaking:** `~/.claude/settings.json` is no longer a symlink to the repository `settings.json` but a regular file merged by ai-rules, so Claude Code no longer writes into the repository. `ai-rules update` migrates a legacy symlink automatically (backup in `$XDG_STATE_HOME/ai-rules/backups/claude/`, keys written by Claude Code are preserved)

### Fixed

### Removed
- `autoApprove` key from `settings.json`: it is not a documented Claude Code setting (`update` removes it from `~/.claude/settings.json` when ai-rules set it)

## [0.6.2] - 2026-11-19

### Added
- `docs/metrics/baseline-0.6.1.md`: reference measurement of the context cost of the rules (`/context` categories, per-file tokens, estimate versus measurement, effect of the first R0 fixes), the comparison point for the roadmap phases
- `scripts/measure-context.sh`: per-layer byte, line and approximate token counts (Claude `@imports`, `rules/` directory, Gemini imports, Codex flat file, plus `core/` and `skills/` when present) as a Markdown table, with `--files` and a double-loading count; covered by `tests/test_measure_context.py`
- `ROADMAP.md`: roadmap 0.6.2 → 1.0.0 (always-on core, scoped rules, skills, hooks, cross-agent parity, evals) with findings, target architecture, phases and acceptance criteria

### Changed
- `ROADMAP.md`, `TODO.md`: roadmap corrected after the 2026-11-19 measurements. F1 uses the measured ~24.5k tokens instead of ~16k; F2 (double loading) is bounded to what was measured (none with the symlink deployment; the real cost was the non-imported template, fixed); the two deployment options are dropped with their reasons; phase 0 renamed "loading hygiene" and its items ticked
- `README.md`: new section explaining how rules are loaded (imports as table of contents, `rules/` auto-loaded in full, one load per file with symlinks, estimated cost)
- `rules/ci-triggers-template.md` moved to `templates/ci-triggers.md`: the `rules/` directory is auto-loaded in every session, so the experimental, non-imported template cost about 2.4k tokens each time; `rules/ci.md` now points to it. Integrity tests require every `rules/` file to be imported
- `rules/versioning.md`, `rules/release.md`: between releases `VERSION` is `X.Y.Z-dev`; the release commit drops the suffix and the first commit of the next version sets the new `-dev` value
- `TODO.md`: points to `ROADMAP.md`, adds the roadmap phases as `R0`–`R8` checklists; the deferred rules compaction and version header items and the duplicated template-validation item are folded into them

### Fixed
- `scripts/measure-context.sh`: token estimate calibrated against `/context` (2.7 bytes per token instead of 4, which under-estimated by about 50 %), overridable with `--bytes-per-token`; the "double-loaded" warning is reworded as an overlap note, since Claude Code loads each file once when imports and `rules/` resolve to the same real path

## [0.6.1] - 2026-10-29

### Added
- CI: `actionlint` 1.7.12 step in the lint job, installed from the upstream release with a pinned SHA256 verified before extraction, as required by `rules/ci.md` (workflow linting, checksum on downloaded binaries)

### Changed
- `TODO.md`: track the standby rulesets, the CI triggers template validation and the rules compaction idea in the backlog
- `rules/release.md`, `rules/git.md`: release commit flow per project profile (strict: `release/X.Y.Z` branch and PR; light: direct commit allowed)
- `README.md`: declare the strict project profile, refresh rule and test counts, list the experimental CI triggers template
- `CONTRIBUTING.md`: merge commit and signed commits expectations

### Fixed
- `README.md`: the post-bump refresh command is `uv sync --extra dev --reinstall-package ai-rules`; plain `uv sync` leaves the editable install metadata stale and `--version` (and the version guard test) report the previous version

## [0.6.0] - 2026-10-29

### Added
- `tests/test_rules_integrity.py`: checks for unpinned action tags in rule examples and for rules neither imported nor marked experimental
- `rules/ci-triggers-template.md` — experimental, not-yet-mandatory CI trigger pattern (scope `push` to `main`/`develop`/conventional branch prefixes, exclude tags, scope `pull_request` to PRs targeting `main`, skip `lint`/`test` via job-level `if:` on docs-only changes without breaking required status checks). Validated once on a real project; apply manually elsewhere to test before folding into `rules/ci.md`

### Changed
- Version single source: `VERSION` is now the only place to bump; the build backend reads it (`pyproject.toml`), `ai_rules.__version__` comes from the installed metadata with a `VERSION` file fallback when run from source. Run `uv sync` after bumping to refresh installed metadata
- `rules/ci.md`: action examples use a pinned-SHA placeholder (consistent with the supply-chain rule); lint/test jobs are tool-agnostic
- `rules/git.md`: project profile moved first and referenced from the `main` protection row
- `rules/release.md`: tag push uses a generic `<remote>`
- `rules/docs.md`: `VERSION` single-source rule allows a documented toolchain exception; first commit follows Conventional Commits unless `init:` is explicitly requested
- `rules/pr.md`: linked issue mandatory in strict profile only
- `rules/git.md`: default merge strategy is now a merge commit (keeps GPG signatures; squash and rebase replace or drop them), `git branch -d` for cleanup, new light/strict project profile (strict by default)
- `rules/versioning.md`, `docs.md`, `review.md`, `release.md`: `VERSION` is bumped only in the release commit
- `rules/pr.md`: merge with a merge commit

### Fixed
- `rules/language.md`: restore the English-only rule for project artifacts, accidentally
  overwritten by test content since 0.4.0 (propagated to the Codex flat file)
- `tests/test_rules_integrity.py`: guard against rule regressions (language rule content,
  `CLAUDE.md` imports pointing to existing files)

## [0.5.0] - 2026-09-01

### Added
- `rules/ci.md`: "Workflow security" section (explicit `permissions:`, `concurrency`
  with `cancel-in-progress`, `pull_request` vs `pull_request_target`,
  `persist-credentials: false`), "Action supply chain" section (pin actions to a
  full commit SHA with a version comment, review pins deliberately, prefer
  GitHub/upstream-maintained actions, verify checksums/signatures on downloaded
  binaries), "Repository settings (GitHub)" section (workflow permissions,
  actions allow-list, required status checks, fork approval policy, secrets
  scoped to trusted workflows), and a `Rules` bullet on linting workflow files
  (`actionlint`) once the workflow surface grows
- `rules/release.md`: pre-release checklist now includes reviewing workflow
  permissions, action pins, and external downloads used in CI

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
