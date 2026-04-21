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
│   │   └── CLAUDE.md       # Claude Code entry point (imports rules via @rules/)
│   ├── codex/
│   │   └── AGENTS.md       # Codex entry point (flat file, generated via `ai-rules generate`)
│   └── gemini/
│       └── GEMINI.md       # Gemini entry point (imports rules via @./rules/)
├── rules/                  # Shared rule files by topic (25 files)
│   ├── principles.md
│   ├── language.md
│   ├── naming.md
│   ├── editor.md
│   ├── quality.md
│   ├── tdd.md
│   ├── testing.md
│   ├── security.md
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
│   ├── git.md
│   ├── commits.md
│   ├── issues.md
│   ├── pr.md
│   ├── review.md
│   ├── ci.md
│   └── release.md
├── scripts/
│   └── extract-changelog.sh  # Extract release notes from CHANGELOG.md
├── bin/
│   └── ai-rules              # Development entry point
├── src/ai_rules/             # Python CLI package
├── tests/                    # Test suite (pytest, 104 tests)
├── .github/workflows/
│   └── ci.yml                # CI pipeline (lint + test + coverage)
├── agents.toml               # Agent registry and link declarations
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
```

### Examples

```bash
# List configured agents
ai-rules list

# Check installation status
ai-rules status
ai-rules status claude

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
4. Skips links that are already correctly in place

| Symlink                    | Source                            |
|----------------------------|-----------------------------------|
| `~/.claude/CLAUDE.md`      | `agents/claude/CLAUDE.md`         |
| `~/.claude/rules`          | `rules/`                          |
| `~/.claude/settings.json`  | `settings.json`                   |
| `~/.codex/AGENTS.md`       | `agents/codex/AGENTS.md`          |
| `~/.gemini/GEMINI.md`      | `agents/gemini/GEMINI.md`         |
| `~/.gemini/rules`          | `rules/`                          |

Config patches applied:

| File                       | Key                    | Value    |
|----------------------------|------------------------|----------|
| `~/.codex/config.toml`     | `project_doc_max_bytes`| `131072` |

### What remove does

`ai-rules remove` is the inverse of `install`:

1. Removes symlinks owned by ai-rules
2. Restores the most recent backup if one exists
3. Reverts config patches (restores `.bak` backup, or removes the patched key)

### Agents without native import support (Codex)

Codex does not support file imports natively. Its entry point is a flat file
generated from the Claude entry point with all imports resolved inline.
Regenerate it after updating any rule file:

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

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

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
