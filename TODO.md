# TODO

> Forward-looking plan (0.6.2 → 1.0.0): see [`ROADMAP.md`](ROADMAP.md) — design, rationale, acceptance criteria. This file is the tracker; roadmap phases are prefixed `R` to avoid clashing with the historical phases below.

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

## Phase 5 — CI/CD hardening
### Versioning
- [x] Single source of truth: `VERSION` read by hatchling, `__version__` derived from metadata (fallback to `VERSION`)
### Rules
- [x] `rules/ci.md`: workflow security (permissions, concurrency, `pull_request` vs `pull_request_target`, `persist-credentials`), action supply chain (SHA pinning, checksums), repository settings (GitHub)
- [x] `rules/release.md`: pre-release checklist now reviews CI permissions/pins/downloads
### Dogfooding
- [x] Apply the new `rules/ci.md` guidance to this repo's own `.github/workflows/ci.yml` (`workflow_dispatch`, `permissions`, `concurrency`, `persist-credentials: false`, SHA-pinned actions with version comments)
- [x] Lint workflow files in CI with `actionlint` (pinned version, checksum-verified download)
### Trigger scoping (experimental)
- [x] `templates/ci-triggers.md` (was `rules/ci-triggers-template.md`) — scope `push`/`pull_request` triggers (branch prefixes, no tags, PR target restricted to `main`), skip `lint`/`test` on docs-only changes via job-level `if:` (not trigger-level `paths-ignore`, to avoid stalling required status checks). Marked experimental — not yet folded into `rules/ci.md`'s mandatory checklist
- [ ] Apply the template to 1-2 more real projects; if it holds up, promote it into `rules/ci.md` as a standing requirement and update `core/git.md`'s branching model section to cross-reference it (fate decided in R8: reference file of the `hardening-ci` skill)

## Roadmap 0.6.2 → 1.0.0 (see ROADMAP.md)
### R0 — Baseline and loading hygiene (0.6.2)
- [x] Integrate `ROADMAP.md` and align this tracker
- [x] Add `scripts/measure-context.sh` (per-layer size table, overlap count)
- [x] Record the baseline in a fresh Claude Code session (`/context`) and compare with the script's estimate: `docs/metrics/baseline-0.6.1.md`
- [x] Calibrate `measure-context.sh` on `/context` (2.7 bytes/token) and reword the overlap warning: baseline of 2026-11-19 shows no double loading (symlink deployment)
- [x] Keep experimental files out of the auto-loaded `rules/` directory: `ci-triggers-template.md` moved to `templates/ci-triggers.md` (~2.4k tokens per session); integrity test requires every `rules/` file to be imported
- [x] Settle the double-loading question: none with the symlink deployment (measured); integrity test = every `rules/` file is imported
- [x] Document the effective loading mechanism in `README.md`
### R1 — Settings hardening (0.6.3, breaking)
- [x] Replace the `settings.json` symlink with a managed JSON merge (generalize `config_patches`), including legacy symlink migration in `update`
- [x] Tighten permissions (`ask` for commit/push/rm/npx/chmod, extended `deny`), drop `autoApprove`
### R2 — Skills infrastructure and transition skills (0.7.0)
- [x] `skill_dirs` link type in `agents.toml` (one symlink per skill; install, update pruning, remove, status)
- [x] Skill format, integrity tests, `ai-rules skills list|status|verify`
- [x] Codex native skills (`~/.agents/skills`), confirmed in a Codex session (`/skills`, `$ai-rules` filter)
- [x] Transition skills with unchanged wording: `ai-rules-starting-a-project`, `ai-rules-quality-dimensions`, `ai-rules-reviewing-changes`, `ai-rules-pull-requests-and-issues` (parity test with their rules)
- [x] Skill listing cost measured with `/context`: ~0.3k tokens for the four skills (`docs/metrics/0.7.0.md`)
- [ ] Observe the trigger quality of the descriptions over the 0.7.0 cycle
### R3 — Core slimming and scoped rules (0.8.0, breaking)
- [x] `core/` (always loaded, ≤ 200 lines / 10 KB) + scoped rules with `paths:` frontmatter + CI size budgets
- [x] Gemini and Codex flat files generated from templates (`flat_source`); skill-owned rules unloaded from `rules/`
- [x] Metrics `docs/metrics/0.8.0.md` with the `/context` measurement after `ai-rules update`
- [x] Check in `/context` that scoped rules load on a matching file (shell script, workflow, `CHANGELOG.md`): recorded in `docs/metrics/0.8.0.md`; broad triggers narrowed (`logging`, `compatibility`, `release`)
- [x] Triggering of `api`, `dependencies`, `tdd`, `testing` measured; narrowed `.sh` and `CHANGELOG.md` rule sets observed (`docs/metrics/0.8.0.md`)
- [ ] Decide whether to narrow `logging` (matches test files via `**/*.py`) and `compatibility` (loads on `pyproject.toml`); rules without a natural file trigger (`tdd`, `release`, `versioning`, ...) are Phase 4 skill candidates
- [ ] Stale top-level link detection (`status` reports, `update` removes links ai-rules no longer declares, like stale skill links)
- [x] Skills index in `CLAUDE.md` (four lines, one per skill, checked by a test)
- [x] Targeted condensation of what `core/` needs to meet its budget, with an invariants test; no global rewrite
- [ ] Language split of `naming`/`error-handling`/`logging` only if measured worthwhile (not done in 0.8.0: scoped rules already load only on matching source files)
### R4 — Process skills adapted from Superpowers (0.9.0)
Scope validated 2026-11-24: ten skills, rewritten (not copied), `derived-from` pinned to Superpowers v7.0.2 (`22f0b46`, MIT verified), no skill commits. Deferred: `using-ai-rules` (R5 hook), `subagent-execution` (after R7 evals), `writing-rules-and-skills` (R7). Gemini does not receive these skills before phase 6.
- [x] PR A: `THIRD_PARTY.md` (MIT notice) and `ai-rules-verification-before-completion`
- [ ] PR B: `ai-rules-systematic-debugging`
- [ ] PR C: `ai-rules-test-driven-development`, `ai-rules-refactoring-and-design` (original skill; **the catalogue of techniques is discussed and validated with the user before any text is written**: KISS, YAGNI, design patterns, hexagonal/DDD/SOLID preferences, code smells and proven refactoring techniques, criteria against over-design), `tdd.md` with an explicit Refactor step and a pointer to the skill
- [ ] PR D: `ai-rules-brainstorming` (with candidate ranking by value and complexity, from `ai-custom`), `ai-rules-writing-plans` (with an initial repository inspection step), `ai-rules-executing-plans`
- [ ] PR E: `ai-rules-receiving-code-review`, `requesting-code-review` merged into `ai-rules-reviewing-changes` with a `review-package` script
- [ ] PR F: `ai-rules-finishing-a-branch`, `ai-rules-releasing` (`release.md` becomes the skill; `changelog.md` and `versioning.md` stay scoped)
- [ ] PR G: `docs/metrics/0.9.0.md`, README, CHANGELOG, listing budget test, release 0.9.0
### R5 — Hooks (0.9.x)
- [ ] `session-start` bootstrap and `pre-tool-guard` (bats-tested, latency budget)
### R6 — Cross-agent parity (0.10.0, breaking)
- [ ] Replace `gemini` by `antigravity`, Codex execution policy, single `permissions.toml` source
- [ ] Embed a rules version header in generated flat files (former deferred item), extend `verify` to skills and scoped outputs
### R7 — Evals and measurement (gate for 1.0.0)
- [ ] `writing-rules-and-skills` with an optimizing-prompts procedure taken from `ai-custom/prompts/ai-engineering-expert.md` (keep the language, never invent requirements, flag ambiguity); archive `ai-custom` afterwards
- [ ] `evals/` with 3 reference tasks, metrics per version in `docs/metrics/`, regression thresholds
### R8 — Wording and consistency cleanup (alongside R2–R4)
- [ ] Project instructions template (from `ai-custom/prompts/templates/project-prompt.md`) as a reference of `ai-rules-starting-a-project`; optional line on shell aliases and completion in `cli.md`
- [ ] Agent-neutral rules, TDD scope clause, single owner per topic, docs refresh, fate of `templates/ci-triggers.md`
- [ ] `tdd.md`: make the Refactor step explicit (after green, review the diff, name what was simplified or state "nothing to refactor")

---

## Future / Postponed
- [ ] Bash installer from GitHub: `curl | bash` one-liner with checksum verification, HTTPS, version pinning — secure installation without cloning the repo
- [ ] Agent coverage: Cursor (`.cursor/rules/*.mdc`), GitHub Copilot (`.github/copilot-instructions.md`), Windsurf (`.windsurfrules`) — not before the R2 skills layer is stable (roadmap non-goal)
- [ ] Agent coverage: Cline / Continue.dev / Aider — investigate config format first
- [ ] `rules/docker.md`: Dockerfile best practices, multi-stage builds, compose conventions
- [ ] `rules/database.md`: migration conventions, naming, indexing, query patterns
- [ ] `rules/python.md`: type hints, dataclasses, async, packaging
- [ ] `rules/frontend.md`: React/Vue conventions, state management, component structure
- [ ] `rules/monitoring.md`: metrics, alerting, observability patterns for services
- [ ] Apply GitHub rulesets to this repo (standby): merge-commit only, signed commits, PR required with 0 approvals (solo), required checks `Lint` / `Test (Python 3.11)` / `Test (Python 3.12)`, semver tag protection `refs/tags/[0-9]*`; depends on new templates in `gh-rulesets`

## Deferred / Under Consideration
- [ ] Web UI or TUI for managing agent installations
- [ ] `rules/performance.md`: profiling, benchmarking, performance budgets
- [ ] `rules/accessibility.md`: a11y standards, ARIA, color contrast
