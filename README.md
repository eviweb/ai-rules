# ai-rules

[![CI](https://github.com/eviweb/ai-rules/actions/workflows/ci.yml/badge.svg)](https://github.com/eviweb/ai-rules/actions/workflows/ci.yml)

Shared rules and conventions for AI coding assistants.

Provides a structured set of rules covering language, naming, git workflow,
security, testing, documentation, and more — applied consistently across all
supported AI assistants.

## Supported assistants

| Key      | Assistant    | Config file               |
|----------|--------------|---------------------------|
| `claude` | Claude Code  | `agents/claude/CLAUDE.md` |

## Structure

```
ai-rules/
├── agents/
│   └── claude/
│       └── CLAUDE.md       # Claude Code entry point (imports rules via @rules/)
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
uv pip install -e .
```

Add `AI_RULES_HOME` to your shell profile so the CLI can locate the repository
from anywhere:

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
  list     List available agents.
  status   Show installation status for one or all agents.
  install  Install rules for one or all agents.
  update   Update installation for one or all agents.
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

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
tests/run-tests.sh
# or
.venv/bin/python3 -m pytest -v
```

## OS support

Tested on Ubuntu 24.04 LTS. Requires Bash 5+ for shell scripts.
