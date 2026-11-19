# Baseline: context cost of the rules (0.6.1 rules, before R0)

Reference measurement for `ROADMAP.md` (phase 0). Later versions are compared against it (`docs/metrics/<version>.md`, phase 7).

## Conditions

| Item | Value |
|------|-------|
| Date | 2026-11-19 |
| Model | `claude-opus-5-5` (token counts depend on the tokenizer) |
| Commit | `7603262` (rules content of 0.6.1 plus the `-dev` wording in `versioning.md` and `release.md`, about 330 bytes, under 1 %) |
| `VERSION` | `0.6.2-dev` |
| Deployment | symlinks: `~/.claude/rules` -> `rules/`, `~/.claude/CLAUDE.md` -> `agents/claude/CLAUDE.md` |
| Method | `/context` in a fresh Claude Code session, run before typing anything; `/memory` returned no data ("Cancelled memory editing"), so memory locations were read from the filesystem |
| Account overhead | MCP server instructions, skills and deferred MCP tools come from the account settings and vary outside this repository |

## Session baseline (`/context`, 61.5k of 1M tokens)

| Category | Tokens | Share of the loaded total |
|----------|--------|---------------------------|
| Memory files (rules, `CLAUDE.md`, auto-memory index) | 27.3k | 44 % |
| System tools | 16.8k | 27 % |
| Skills (36) | 6.6k | 11 % |
| MCP server instructions | 5.7k | 9 % |
| System prompt | 4.4k | 7 % |
| MCP tools (loaded) | 0.7k | 1 % |
| Messages | 0.01k | 0 % |

Not counted because deferred: MCP tools (269.7k), system tools (23.5k).

## Memory files: 28 files, 27.3k tokens

- `~/.claude/CLAUDE.md`: 296 tokens (imports 25 rule files)
- `~/.claude/rules/`: 26 files, about 26.8k tokens; the directory is auto-loaded in full, so `ci-triggers-template.md` (not imported) was loaded too
- Auto-memory index (`MEMORY.md`): 127 tokens
- Each rule file is listed once: the imports and the auto-loaded directory resolve to the same real paths, so there is no double loading with the symlink deployment

## Rules, per file

`/context` rounds to 0.1k (about 50 tokens).

| File | Bytes | Tokens (`/context`) | Bytes per token |
|------|-------|---------------------|-----------------|
| `rules/quality.md` | 8,208 | 2.6k | 3.16 |
| `rules/ci-triggers-template.md` | 6,196 | 2.4k | 2.58 |
| `rules/ci.md` | 5,837 | 2.3k | 2.54 |
| `rules/api.md` | 5,248 | 2.0k | 2.62 |
| `rules/testing.md` | 4,956 | 1.9k | 2.61 |
| `rules/docs.md` | 4,667 | 1.8k | 2.59 |
| `rules/git.md` | 4,602 | 1.7k | 2.71 |
| `rules/error-handling.md` | 4,312 | 1.6k | 2.69 |
| `rules/compatibility.md` | 3,049 | 1.3k | 2.35 |
| `rules/cli.md` | 2,974 | 1.1k | 2.70 |
| `rules/logging.md` | 2,904 | 1.1k | 2.64 |
| `rules/release.md` | 2,709 | 1.2k | 2.26 |
| `rules/naming.md` | 2,671 | 1.1k | 2.43 |
| `rules/principles.md` | 2,208 | 678 | 3.26 |
| `rules/commits.md` | 1,917 | 682 | 2.81 |
| `rules/review.md` | 1,773 | 668 | 2.65 |
| `rules/security.md` | 1,747 | 585 | 2.99 |
| `rules/shell.md` | 959 | 366 | 2.62 |
| `rules/changelog.md` | 796 | 315 | 2.53 |
| `rules/tdd.md` | 765 | 266 | 2.88 |
| `rules/issues.md` | 631 | 226 | 2.79 |
| `rules/pr.md` | 619 | 223 | 2.78 |
| `rules/versioning.md` | 609 | 254 | 2.40 |
| `rules/editor.md` | 541 | 218 | 2.48 |
| `rules/dependencies.md` | 529 | 180 | 2.94 |
| `rules/language.md` | 253 | 76 | 3.33 |
| **Total `rules/`** | **71,680** | **about 26.8k** | **2.67** |

The per-file figures add up to the directory total reported by `/context`.

## Estimate of `scripts/measure-context.sh` against `/context`

| Formula | `rules/` estimate | `/context` | Error |
|---------|-------------------|------------|-------|
| bytes / 4 (initial) | 17,920 | about 26.8k | -33 % |
| bytes / 2.7 (calibrated) | 26,548 | about 26.8k | -1 % |

The 2.7 ratio was derived from this run. Per-file ratios range from 2.3 to 3.3 bytes per token (prose is dense, tables and code blocks are not), so the estimate holds for layer totals but not for ranking files of similar size.

## After the first R0 fixes (second run)

Commit `ebaf4a9`: calibrated script and `ci-triggers-template.md` moved from `rules/` to `templates/`.

| Category | Run 1 | Run 2 | Change |
|----------|-------|-------|--------|
| Memory files | 27.3k | 24.9k | -2.4k |
| Total loaded | 61.5k | 59.7k | -1.8k |

The calibration was validated on this different file set: the script gives 24,304 tokens for `rules/` (65,619 bytes, 25 files) against about 24.5k measured (+/- 1 %). The other categories moved by 0.1k to 0.4k, which is session noise (system prompt, tools, skills).

## Reproduce

```bash
scripts/measure-context.sh --files   # byte-based estimate, 2.7 bytes per token
# then, in a fresh Claude Code session:
/context                             # authoritative token counts
```

Subtract `~/.claude/CLAUDE.md` (about 0.3k) and the auto-memory index (about 0.1k) from the memory files total to get the rules alone.
