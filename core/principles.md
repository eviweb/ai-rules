# General Coding Principles

## Analyze before coding
Always read and understand the relevant code before writing or modifying anything. Never edit a file that has not been read first. If the scope is unclear, ask before proceeding.

## Propose before implementing
For any non-trivial change, describe the intended approach and wait for explicit validation before writing code. This avoids costly back-and-forth on the wrong solution.

## Clarify before starting
If a request is ambiguous, incomplete, or could be interpreted in multiple ways, ask for clarification before writing any code. Starting on a wrong assumption wastes more time than a single clarifying question.

## Propose options before deciding
For any structuring choice (architecture, tooling, git strategy, framework, etc.), present the available options with their trade-offs and wait for explicit validation before proceeding. Never make a significant design decision autonomously.

## Prefer minimal diffs
Make the smallest change that correctly solves the problem. Do not touch code outside the scope of the request, even to fix style or improve readability.

## No refactoring without explicit request
Never restructure, rename, or reorganize code outside the current change unless the user has asked for it. The Refactor step of TDD applies to the code this change writes or modifies. Anything else you notice: report it (what, where, why) and propose it separately; do not do it in passing. Refactoring mixed with feature changes makes review harder and increases risk.

## No speculative additions
Do not add features, options, abstractions, or error handling for hypothetical future needs. Implement only what is currently required.

## No dead code
Do not leave commented-out code, unused variables, or untracked TODOs. Either resolve them or open a tracked issue. Before removing code that looks unused or odd (a guard, a workaround, a pin, a config entry, a CI step), find out why it exists: history, callers, tests. If you cannot tell, ask or leave it.

## Confirm before irreversible actions
Any action that is hard or impossible to undo (file deletion, branch deletion, `git reset --hard`, force-push, database drop, etc.) must be explicitly described to the user and confirmed before execution. Never perform destructive operations autonomously.

## Explicit naming
Names for functions, methods, classes, variables, and files must be as explicit as possible. Prefer clarity over brevity: a longer name that describes intent precisely is always better than a short name that requires context to understand.
