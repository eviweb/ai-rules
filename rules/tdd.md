---
paths:
  - "tests/**"
  - "**/test_*.py"
  - "**/*.test.{js,ts}"
  - "**/*_test.go"
  - "**/*.bats"
---
# Test-Driven Development

> **TDD is mandatory** for code with testable behavior: every feature, fix or refactor is driven by tests. Configuration and infrastructure changes have no unit test; they are verified instead (`ai-rules-verification-before-completion`).

At the start of a project, propose one or more suitable test frameworks with a clear recommendation. Use the framework validated by the user throughout the project.

- Follow the Red-Green-Refactor cycle: write a failing test first, watch it fail for the expected reason, make it pass with minimal code, then refactor.
- **Refactor is a step, not an option.** After green, review the diff: remove duplication, improve names, simplify. If nothing needs changing, say "nothing to refactor" and why. The scope is the code written in this cycle and its immediate surroundings; a wider restructuring is proposed to the user with its justification, not done in passing.
- Never ship code without a corresponding test. If code was written before its test, say so and propose to redo it test-first.
- Keep tests in a `tests/` directory with a dedicated runner script.
- For shell scripts: bats-core is the standard choice.
- Do not skip or defer tests: if a test is hard to write, it signals a design problem to fix first.

Procedure and examples: `ai-rules-test-driven-development`. Refactoring signals and techniques: `ai-rules-refactoring-and-design`.
