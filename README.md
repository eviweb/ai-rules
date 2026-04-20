# ai-rules

[![CI](https://github.com/eviweb/ai-rules/actions/workflows/ci.yml/badge.svg)](https://github.com/eviweb/ai-rules/actions/workflows/ci.yml)

Shared rules and conventions for AI coding assistants.

Provides a structured set of rules covering language, naming, git workflow,
security, testing, documentation, and more — applied consistently across all
supported AI assistants.

## Supported assistants

| Key      | Assistant    | Config file                   | Import support |
|----------|--------------|-------------------------------|----------------|
| `claude` | Claude Code  | `agents/claude/CLAUDE.md`     | native         |
| `codex`  | Codex        | `agents/codex/AGENTS.md`      | flat file      |

## Structure

```
ai-rules/
├── agents/
│   ├── claude/
│   │   └── CLAUDE.md       # Claude Code entry point (imports rules via @rules/)
│   └── codex/
│       └── AGENTS.md       # Codex entry point (flat file, generated via `ai-rules generate`)
├── rules/                  # Shared rule files by topic
│   ├── principles.md
│   ├── language.md
│   ├── naming.md
│   ├── editor.md
│   ├── tdd.md
│   ├── security.md
│   ├── dependencies.md
│   ├── compatibility.md
│   ├── docs.md
│   ├── changelog.md
│   ├── versioning.md
│   ├── shell.md
│   ├── cli.md
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
├── tests/                    # Test suite (pytest)
├── .github/workflows/
│   └── ci.yml                # CI pipeline (lint + test)
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
  -V, --version   Show version and exit.
  --help          Show this message and exit.

Commands:
  list      List available agents.
  status    Show installation status for one or all agents.
  install   Install rules for one or all agents.
  update    Update installation for one or all agents.
  generate  Generate flat rule files for agents without native import support.
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

# Regenerate flat files for agents without native import support
ai-rules generate
ai-rules generate codex

# Shell completion (bash/zsh/fish)
ai-rules --install-completion
```

### What install does

For each declared link in `agents.toml`, `ai-rules install`:

1. Creates a symlink in the agent's `install_dir`
2. Backs up any existing non-symlink file before replacing it
3. Skips links that are already correctly in place

| Symlink                    | Source                            |
|----------------------------|-----------------------------------|
| `~/.claude/CLAUDE.md`      | `agents/claude/CLAUDE.md`         |
| `~/.claude/rules`          | `rules/`                          |
| `~/.claude/settings.json`  | `settings.json`                   |
| `~/.codex/AGENTS.md`       | `agents/codex/AGENTS.md`          |

### Agents without native import support (Codex)

Codex does not support `@rules/` imports natively. Its entry point is a flat
file generated from the Claude entry point with all imports resolved inline.
Regenerate it after updating any rule file:

```bash
ai-rules generate codex
```

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
