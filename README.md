# ai-rules

[![CI](https://github.com/eviweb/ai-rules/actions/workflows/ci.yml/badge.svg)](https://github.com/eviweb/ai-rules/actions/workflows/ci.yml)

Shared rules and conventions for AI coding assistants.

Provides a structured set of rules covering language, naming, git workflow,
security, testing, documentation, and more — applied consistently across all
supported AI assistants.

## Supported assistants

| Key      | Assistant    | Config file                   | Import support  |
|----------|--------------|-------------------------------|-----------------|
| `claude` | Claude Code  | `agents/claude/CLAUDE.md`     | native          |
| `codex`  | Codex        | `agents/codex/AGENTS.md`      | flat file       |
| `gemini` | Gemini       | `agents/gemini/GEMINI.md`     | native          |

## Structure

```
ai-rules/
├── agents/
│   ├── claude/
│   │   └── CLAUDE.md       # Claude Code entry point (imports the core only)
│   ├── codex/
│   │   ├── AGENTS.md       # Codex entry point (flat file, generated via `ai-rules generate`)
│   │   └── AGENTS.src.md   # Template of the Codex flat file (core and scoped rules)
│   └── gemini/
│       ├── GEMINI.md       # Gemini entry point (flat file, generated from GEMINI.src.md)
│       └── GEMINI.src.md   # Template of the Gemini flat file (core, rules and skill texts)
├── core/                   # Always-loaded core rules (5 files, ≤ 200 lines / 10 KiB)
├── rules/                  # Scoped rules (15 files, `paths:` frontmatter, loaded when a matching file is touched)
│   ├── naming.md
│   ├── tdd.md
│   ├── testing.md
│   ├── dependencies.md
│   ├── compatibility.md
│   ├── docs.md
│   ├── changelog.md
│   ├── versioning.md
│   ├── shell.md
│   ├── cli.md
│   ├── logging.md
│   ├── error-handling.md
│   ├── api.md
│   ├── ci.md
│   └── release.md
├── skills/                 # Skills (ai-rules-<topic>/SKILL.md), loaded on demand; see docs/skills.md
├── templates/              # On-demand references, not auto-loaded
│   └── ci-triggers.md      # experimental CI triggers pattern
├── docs/
│   ├── metrics/            # Context-cost measurements per version (baseline-0.6.1.md, 0.7.0.md, 0.8.0.md)
│   ├── skills.md           # How to write a skill (format, description style, derived skills)
│   └── sources.md          # Register of the standards and upstream projects relied on, with review dates
├── scripts/
│   ├── extract-changelog.sh  # Extract release notes from CHANGELOG.md
│   ├── measure-context.sh    # Size of each rule-loading layer (bytes, lines, ~tokens)
│   └── check-sources-age.sh  # Lists the sources of docs/sources.md that are due for a review
├── bin/
│   └── ai-rules              # Development entry point
├── src/ai_rules/             # Python CLI package
├── tests/                    # Test suite (pytest, 456 tests)
├── .github/workflows/
│   ├── ci.yml                # CI pipeline (lint + test + coverage)
│   └── sources-review.yml    # Monthly check of docs/sources.md; opens an issue when sources are due
├── agents.toml               # Agent registry and link declarations
├── THIRD_PARTY.md            # Notices for the upstream projects some skills are derived from
└── pyproject.toml            # Python package definition
```

## Requirements

- Python 3.11+
- [pipx](https://pipx.pypa.io) (recommended) or [uv](https://github.com/astral-sh/uv)

## Installation

```bash
git clone git@github.com:eviweb/ai-rules.git

# Install with pipx (isolated, globally available)
pipx install ./ai-rules

# Or with uv (for development)
cd ai-rules
uv sync
```

### Shell wrapper (symlink-friendly)

`bin/ai-rules-wrapper` is a bash entry point that works from any directory,
including when installed via symlink. It resolves the repository root
automatically (no `AI_RULES_HOME` required):

```bash
ln -s /path/to/ai-rules/bin/ai-rules-wrapper ~/.local/bin/ai-rules
```

If you prefer to set `AI_RULES_HOME` explicitly (e.g. in your shell profile),
the wrapper will use it instead of auto-detection:

```bash
export AI_RULES_HOME=~/path/to/ai-rules
```

## Usage

```
ai-rules [OPTIONS] COMMAND [ARGS]

Options:
  -V, --version            Show version and exit.
  -v, --verbose            Enable verbose output.
  -q, --quiet              Suppress non-error output.
  --debug                  Enable debug mode.
  --no-color               Disable colored output.
  --no-log                 Disable file logging.
  --log-dir PATH           Override the default log directory.
  --help                   Show this message and exit.

Commands:
  list      List available agents.
  status    Show installation status for one or all agents.
  install   Install rules for one or all agents.
  update    Update installation and regenerate flat files for one or all agents.
  remove    Remove rules for one or all agents, restoring original configuration.
  generate  Generate flat rule files for agents without native import support.
  verify    Verify flat rule files are in sync with current rules.
  skills    Inspect and verify the skills shipped by this repository.
```

### Examples

```bash
# List configured agents
ai-rules list

# Check installation status
ai-rules status
ai-rules status claude

# Skills: list, check the format rules (exit 1 on any problem), deployment state
ai-rules skills list
ai-rules skills verify
ai-rules skills status

# Install all agents
ai-rules install

# Install a specific agent
ai-rules install claude

# Dry run
ai-rules install --dry-run

# Update after pulling new rules (redeploys symlinks + regenerates flat files)
ai-rules update

# Remove all agents, restoring original configuration
ai-rules remove
ai-rules remove codex

# Regenerate flat files for agents without native import support
ai-rules generate
ai-rules generate codex

# Verify flat files are in sync (useful in CI)
ai-rules verify

# Shell completion (bash/zsh/fish)
ai-rules --install-completion
```

### What install does

For each declared link in `agents.toml`, `ai-rules install`:

1. Creates a symlink in the agent's `install_dir`
2. Backs up any existing non-symlink file before replacing it
3. Applies config patches (updates specific keys in existing config files)
4. Merges settings files key by key (see below)
5. Skips links that are already correctly in place
6. Links skill folders one by one (see below)

| Symlink                    | Source                            |
|----------------------------|-----------------------------------|
| `~/.claude/CLAUDE.md`      | `agents/claude/CLAUDE.md`         |
| `~/.claude/rules`          | `rules/`                          |
| `~/.codex/AGENTS.md`       | `agents/codex/AGENTS.md`          |
| `~/.gemini/GEMINI.md`      | `agents/gemini/GEMINI.md`         |

Config patches applied:

| File                       | Key                    | Value    |
|----------------------------|------------------------|----------|
| `~/.codex/config.toml`     | `project_doc_max_bytes`| `131072` |

Settings merge (`[[agents.*.settings_merge]]` in `agents.toml`):

| File                       | Fragment        | Keys owned by ai-rules                                      |
|----------------------------|-----------------|-------------------------------------------------------------|
| `~/.claude/settings.json`  | `settings.json` | `permissions.allow`, `permissions.ask`, `permissions.deny`, `hooks` |

`~/.claude/settings.json` is a regular file, not a symlink: Claude Code writes its own keys into it (plugins, `/permissions`, theme), which would otherwise land in this repository. ai-rules adds its list entries and scalars (`allow`, `ask` and `deny` rules; `git commit`, `git push`, `rm`, `npx` and `chmod` ask first, destructive variants such as `rm -r`, `git push --force`, `git reset --hard` and `git clean` are denied, `--force-with-lease` still asks), never touches other keys, and records what it added in `$XDG_STATE_HOME/ai-rules/state/claude-settings.json`. `ai-rules update` retires entries that left the fragment. A legacy symlinked install is migrated automatically: the content is backed up to `$XDG_STATE_HOME/ai-rules/backups/claude/` and replaced by a regular file with the same content.

Skill directories (`[[agents.*.skill_dirs]]` in `agents.toml`): each sub-folder of `source` that holds a `SKILL.md` is linked to `<install_dir>/<target>/<folder name>`, one symlink per skill, so skills you write yourself live in the same directory and are never touched. `ai-rules update` unlinks the skills that were deleted from the repository (only symlinks pointing into the source directory are considered ai-rules', never other entries); a real folder with the same name is backed up first. `status` lists one line per skill (`ok`, `not installed`, `symlink mismatch`, `exists (not a symlink)`, `stale`). Claude Code links them under `~/.claude/skills/` and Codex under `~/.agents/skills/` (the user skills directory Codex scans); a target starting with `~` or an absolute path is not relative to `install_dir`. Gemini has no skills yet (phase 6).

### What remove does

`ai-rules remove` is the inverse of `install`:

1. Removes symlinks owned by ai-rules
2. Restores the most recent backup if one exists
3. Reverts config patches (restores `.bak` backup, or removes the patched key)
4. Reverts settings merges: removes only the entries ai-rules added and restores the scalars it replaced (the file is deleted if it ends up empty)
5. Unlinks the skills deployed by ai-rules and restores a backed-up folder of the same name; other skills are left alone

### How rules are loaded (Claude Code)

- `~/.claude/CLAUDE.md` imports only the core (`@../../core/<name>.md`): five files, always in context. Claude Code resolves a relative import against the **real path** of the file that holds it, and `~/.claude/CLAUDE.md` is a symlink into this repository, so the paths are written relative to `agents/claude/` (checked by a test). `@core/…` would look for `agents/claude/core/` and silently load nothing.
- `~/.claude/rules/` holds the topic rules. Each has a `paths:` frontmatter, so Claude Code loads it only when it reads or writes a matching file (patterns are relative to the session's working directory). A rule is never imported: an `@import` always loads its file. The tests enforce both.
- Task-type material (project start, quality dimensions, review, pull requests and issues) lives in skills, loaded on demand; Codex and Gemini receive the same texts in their generated flat files (Gemini has no skills; Codex has native skills for them).
- Always-on cost: the core is about 9.5 KB (about 3.5k tokens) plus the skill listing (about 0.3k). Estimate it with `scripts/measure-context.sh` and confirm with `/context`.
- Migration from 0.7.x: run `ai-rules update`. The `~/.claude/core` (0.8.0-dev builds only), `~/.gemini/core` and `~/.gemini/rules` links are not used and can be deleted by hand.

### Agents with a generated flat file (Codex, Gemini)

Codex and Gemini load a single flat file. Each is generated from its template
(`flat_source` in `agents.toml`: `agents/codex/AGENTS.src.md`,
`agents/gemini/GEMINI.src.md`) with every `@core/`, `@rules/` and `@skills/`
line resolved inline, frontmatter removed and each scoped rule introduced by a
one-line "Applies when working on" note. Codex gets the core and the scoped rules
(its native skills carry the rest); Gemini, which has no skills, also gets the
skill texts. Regenerate after updating any rule or skill:

```bash
ai-rules generate codex
# or simply:
ai-rules update codex
```

Verify the flat file is in sync (e.g. in CI):

```bash
ai-rules verify
```

## XDG Base Directory paths

ai-rules follows the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/). All files it writes on the user's machine respect XDG defaults:

| Purpose | Path | Default |
|---------|------|---------|
| Backups (link files) | `$XDG_STATE_HOME/ai-rules/backups/<agent>/backup-<ts>/` | `~/.local/state/ai-rules/backups/<agent>/backup-<ts>/` |
| Backups (config patches) | `$XDG_STATE_HOME/ai-rules/backups/<agent>/` | `~/.local/state/ai-rules/backups/<agent>/` |
| Logs | `$XDG_STATE_HOME/ai-rules/logs/` | `~/.local/state/ai-rules/logs/` |

Log filename format: `ai-rules-YYYY-MM-DD.log`. File logging is enabled by default; disable with `--no-log` or override the directory with `--log-dir <path>`.

If upgrading from a version that stored backups in the agent install dirs (`~/.claude/backup-*/`, `~/.codex/*.bak`), run `ai-rules update` once to migrate them automatically.

## Project profile

`ai-rules` follows the **strict** profile defined in `core/git.md`: every change goes through a pull request, merged with a merge commit (`gh pr merge --merge`) so that commit signatures are preserved, with CI required on `main`. Releases are bumped only in the release commit (`VERSION` is the single source of the version).

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# After changing VERSION, refresh the installed metadata so `--version` matches
# (plain `uv sync` keeps the stale metadata of the editable install)
uv sync --extra dev --reinstall-package ai-rules

# Install git hooks (regenerates flat files automatically on commit)
ln -sf ../../scripts/pre-commit .git/hooks/pre-commit

# Run tests
tests/run-tests.sh
# or
uv run pytest -v
```

## OS support

| Platform | Status |
|----------|--------|
| Ubuntu 22.04 LTS | supported |
| Ubuntu 24.04 LTS | supported (primary) |
| Termux (Android) | supported |

Requires Bash 5+ and zsh for shell scripts. No `sudo` needed — all files are installed in user directories.
