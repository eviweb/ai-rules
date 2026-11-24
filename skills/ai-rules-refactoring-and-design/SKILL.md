---
name: ai-rules-refactoring-and-design
description: "Use when the Refactor step of a TDD cycle is reached, when smells or hard-to-change code are noticed, or when choosing a design or pattern: smell scan, safe refactoring steps, and reporting deeper structural problems."
---
# Refactoring and design

Keep code simple and cheap to change. Refactoring changes structure, never behavior. Use this skill at the Refactor step of every TDD cycle, when you meet code that resists change, and when a design or pattern is being chosen.

## Arbiters, in this order

1. **Correct**: behavior preserved, tests green.
2. **Simple** (KISS, YAGNI; `core/principles.md`): the least structure that satisfies today's need.
3. **Readable**: explicit names, small units, one level of abstraction per function.
4. **DRY**: remove duplicated *knowledge*, at the third occurrence, not look-alikes.
5. **Patterns and architecture**: last, and only when a real force calls for them.

When two arbiters conflict, the lower number wins.

## Two hats, Chesterton's fence

- Never mix a refactoring with a feature or a fix in the same step or commit. Finish the behavior change on green, then refactor; or refactor first as preparation ("make the change easy, then make the easy change"), in its own commit. Propose the commit boundaries; never commit (`core/commits.md`).
- Before removing or rewriting code that looks pointless, find out why it exists (`git log -S`, `git blame`, tests, callers). If you cannot tell, ask or leave it.
- **Notice and report**: a defect you see outside the code of this change is not fixed in passing. Note what, where and why, and propose a separate cleanup.

## The Refactor step (after green)

1. Scan the code this cycle writes or modifies with the table below.
2. Pick one smell, apply the smallest technique, run the tests, repeat. Stop when the scan is clean or what remains is outside this scope.
3. No test around the code you want to change? Write a characterization test that pins today's behavior first ([legacy techniques](references/refactorings.md)).
4. Report what changed and why, or say "nothing to refactor" and why.

| Signal | Technique |
|--------|-----------|
| Duplicated knowledge | Extract Function, Pull Up, Parameterize Function |
| Long function, comment explaining a block | Extract Function, Decompose Conditional, Replace Temp with Query |
| Deep nesting | Guard clauses, Decompose Conditional |
| Long parameter list, data clumps | Introduce Parameter Object, Preserve Whole Object |
| Same switch or if-chain on a type in several places | Replace Conditional with Polymorphism, Strategy |
| Feature envy, message chains | Move Function, Hide Delegate |
| Primitive obsession | Replace Primitive with Object (value object) |
| Flag argument | Remove Flag Argument (split the function) |
| Mysterious name | Rename |
| Dead code, speculative generality | Remove Dead Code, Inline Function or Class |
| Shared mutable or global data | Encapsulate Variable, immutability |
| Large class, divergent change | Extract Class |

Full lists: [smells](references/smells.md), [techniques](references/refactorings.md). Thresholds are hints, not rules, and the project's linter configuration wins when there is one ([smells](references/smells.md)). A smell in stable code nobody reads is not worth a change.

## Deeper structural problems: report, never fix in passing

Signals: **shotgun surgery** (one change touches many places), **divergent change** (one module changes for unrelated reasons), a god object or module, circular dependencies, boundaries or layers in the wrong place, code that cannot be tested without heavy mocking, the same area breaking again and again, three failed fixes (`ai-rules-systematic-debugging`).

Say so explicitly, with a **refactoring proposal**:

- **Finding**: what, with evidence (files, lines, how often it changed in `git log`, missing tests).
- **Why now**: the cost observed (slower changes, repeated bugs).
- **Options**: do nothing, a small step, the larger refactoring; for each the effort, risk and reversibility.
- **Technique**: Parallel Change, Strangler Fig, Branch by Abstraction or Mikado; the characterization test to write first; the steps as separate commits.
- **Recommendation**, then wait for the user's decision. If deferred, record it as debt according to the project profile (`core/git.md`): light, a `[debt]` line in `TODO.md` under Future / Postponed carrying the fields above; strict, an issue (`ai-rules-pull-requests-and-issues`) plus a `TODO.md` line linking to it. Ask before creating an issue. Remove the entry when done.

## Design choices

Apply a pattern only when its problem is present, found through [patterns](references/patterns.md) (an index of all 23 GoF patterns; eight rarer ones are detailed on request in `references/patterns-extra.md`). Patterns usually emerge from refactoring; do not plan them in advance. Principles (SOLID, cohesion, composition, Tell don't ask, CQS, functional core): [principles](references/principles.md). Choosing an architecture: `ai-rules-architecture-proposal`. Accessibility, privacy, security and other quality concerns: `ai-rules-quality-dimensions`.

## Stack specifics

Detect the project's languages from its manifests and read only the matching file: language idioms, smells specific to it, and detectors (linters, analysers, automated refactoring). Propose a tool the project does not use yet; never add it silently.

| Manifest or files | Read |
|-------------------|------|
| `*.sh`, `bin/` scripts | [shell](references/stacks/shell.md) |
| `pyproject.toml`, `*.py` | [Python](references/stacks/python.md) |
| `package.json`, `tsconfig.json` | [JS/TS](references/stacks/js-ts.md) |
| `go.mod` | [Go](references/stacks/go.md) |
| `Cargo.toml` | [Rust](references/stacks/rust.md) |
| `composer.json` | [PHP](references/stacks/php.md) |
| any | [common tools](references/stacks/common.md) |

## In ai-rules

This skill changes code only within the Refactor scope above (`core/principles.md` forbids restructuring outside the current change; anything wider is reported and proposed first) and never commits.
