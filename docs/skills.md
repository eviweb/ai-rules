# Writing skills

A skill is a folder `skills/ai-rules-<topic>/` loaded on demand by the agent. Its name and description sit in the agent's context at every turn; the body is read only when the skill triggers. Keep the description sharp and the body short.

Check your work with `ai-rules skills verify` (the same checks run in the test suite and in CI).

## Layout

```
skills/ai-rules-<topic>/
├── SKILL.md          # required: frontmatter + instructions (≤ 8 KiB)
├── references/       # optional: longer material, read on demand
└── scripts/          # optional: executable helpers, shellcheck-clean
```

A folder without a `SKILL.md` is reported as a problem by `verify` and ignored by `install`.

## Frontmatter

```yaml
---
name: ai-rules-reviewing-changes
description: Use when about to commit, open a pull request, or review a change; checklists for code, tests, docs and security.
---
```

| Field | Rule |
|-------|------|
| `name` | Required. Equals the folder name, starts with `ai-rules-`, kebab-case, at most 64 characters |
| `description` | Required. Starts with `Use when`, at most 300 characters. Say **when** to use the skill, not what it contains; put the trigger first |
| `license`, `compatibility`, `allowed-tools` | Optional, as defined by the Agent Skills format |
| `metadata` | Optional mapping of string values (one level) |

Only these fields are accepted: they are the ones understood by Claude Code, claude.ai and the standard format. Claude Code–specific fields can be allowed when a skill needs one.

The frontmatter is parsed by a small strict YAML subset: `key: value`, plain or quoted scalars, one level of `metadata`. Quote any value that contains `: ` or ` #`; folded blocks (`>`), lists and escapes are rejected. A plain YAML parser (the agent's) would choke on those values and load the skill without its fields.

## Skills derived from another project

A skill rewritten from an upstream skill (for example from Superpowers) records its origin:

```yaml
metadata:
  derived-from: "superpowers/test-driven-development @ <commit or version>"
  license-of-origin: MIT
```

`verify` then requires a `THIRD_PARTY.md` at the repository root that names the upstream project (copyright and license text). Verify the upstream license before copying anything.

## References and scripts

- Link longer material with a relative path (`[details](references/details.md)`) or a backticked path (`` `scripts/check.sh` ``): the file must exist and stay inside the skill folder.
- Files under `scripts/` are executable and, when they are shell scripts, pass `shellcheck` (skipped if `shellcheck` is not installed).

## Deployment

`ai-rules install` / `update` symlink each skill folder into the agent's skills directory (`~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex), one link per skill; skills you write yourself are never touched. `ai-rules status` and `ai-rules skills status` show the state.
