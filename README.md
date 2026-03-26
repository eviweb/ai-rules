# claude-config

Global [Claude Code](https://claude.ai/claude-code) configuration — rules and conventions applied to all projects.

## Structure

```
claude-config/
├── CLAUDE.md        # Entry point loaded by Claude Code, imports all rule files
├── settings.json    # Claude Code global permissions
├── rules/           # Individual rule files by topic
│   ├── language.md
│   ├── naming.md
│   ├── editor.md
│   ├── principles.md
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
| `~/.claude/settings.json` | `claude-config/settings.json` |

Existing files are backed up automatically before being replaced.

## Options

```
./install.sh [options]

  -h, --help      Display help
  -n, --dry-run   Simulate without making changes
  -v, --verbose   Enable verbose output
```
