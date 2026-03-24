# claude-config

Global [Claude Code](https://claude.ai/claude-code) configuration — rules and conventions applied to all projects.

## Structure

```
claude-config/
├── CLAUDE.md        # Entry point loaded by Claude Code, imports all rule files
├── rules/           # Individual rule files by topic
│   ├── language.md
│   ├── tdd.md
│   ├── docs.md
│   ├── commits.md
│   ├── shell.md
│   ├── versioning.md
│   ├── security.md
│   ├── cli.md
│   ├── git.md
│   ├── ci.md
│   ├── release.md
│   ├── dependencies.md
│   ├── issues.md
│   ├── pr.md
│   ├── changelog.md
│   ├── editor.md
│   ├── review.md
│   ├── naming.md
│   └── compatibility.md
└── install.sh       # Deploys symlinks into ~/.claude/
```

## Installation

```bash
git clone <repo-url> ~/remote/git/projects/ia/claude/claude-config
cd claude-config
./install.sh
```

The install script creates the following symlinks:

| Symlink | Target |
|---------|--------|
| `~/.claude/CLAUDE.md` | `claude-config/CLAUDE.md` |
| `~/.claude/rules` | `claude-config/rules/` |

Existing files are backed up automatically before being replaced.

## Options

```
./install.sh [options]

  -h, --help      Display help
  -n, --dry-run   Simulate without making changes
  -v, --verbose   Enable verbose output
```
