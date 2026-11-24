---
name: ai-rules-test-driven-development
description: "Use when implementing a feature, a bug fix or a behavior change, before writing the production code: write one failing test, watch it fail, make it pass with the least code, then refactor."
metadata:
  derived-from: "superpowers/test-driven-development @ 22f0b46"
  license-of-origin: MIT
---
# Test-driven development

Write the test first and watch it fail. A test you never saw fail proves nothing: it may test the wrong thing, or nothing. Every feature, bug fix and behavior change follows the cycle below.

## Scope

- Applies to code with testable behavior: features, fixes, refactoring, behavior changes.
- Configuration and infrastructure changes have no unit test. Verify them instead (syntax check, dry run, service status; see `ai-rules-verification-before-completion`).
- Throwaway prototypes and generated code are exceptions only when the user agrees.

## The cycle

1. **Red.** Write one small test for one behavior, with a name that states it. Use real code; mock only what you cannot avoid (the network, the clock, a third party).
2. **Verify red.** Run it. It must fail, with the message you expected, because the behavior is missing, not because of a typo or a broken setup. If it passes, it tests something that already exists: fix the test. If it errors, fix the error and run again.
3. **Green.** Write the simplest code that passes. No extra options, no neighbouring clean-up, nothing the test does not ask for (YAGNI).
4. **Verify green.** Run the whole suite, not only the new test. Everything passes and the output is clean. If the new test fails, fix the code, not the test. Any failure in the run, even an older one, is reported by name.
5. **Refactor.** Only on green, and not optional. Review the diff you just made: duplication, names, long or nested functions, a design that fought the test. Keep the tests green after each small step and add no behavior. If nothing needs changing, say "nothing to refactor" and give the reason. The scope is the code of this cycle and its immediate surroundings. If you see a deeper problem (a structure that makes every change hard), say so explicitly with the evidence and propose the refactoring, as described in `ai-rules-refactoring-and-design`; do not do it in passing.
6. **Repeat** with the next failing test.

## A good test

- One behavior. A name containing "and" is two tests.
- The name describes the scenario and the expected outcome (`testing.md`: `test_<unit>_<scenario>_<expected>`).
- Shows the intended API: the test is the first user of the code.
- Asserts on real behavior, not on what a mock was told to return.
- Before writing it, name the production change that would make it fail.

## Bugs

Reproduce the bug with a failing test first, then run the cycle. The test proves the fix and stays as the regression guard. Never fix a bug without one. For a cause you do not understand yet, investigate first (`ai-rules-systematic-debugging`).

## Code written before its test

Do not keep it as a silent exception. Tell the user that the production code came first and propose to redo it test-first (write the test, watch it fail, then reintroduce the code). The decision is the user's.

## When it is hard to test

A test that is hard to write signals a design problem: too much coupling, hidden dependencies, too many responsibilities. Write the assertion you wish you could write, then change the design until you can (inject the dependency, extract a pure function). Ask the user if the right shape is unclear.

## Red flags: stop and go back to red

Code before a test. A test that passes immediately. No idea why the test failed. "I'll add the tests afterwards". "Already tested by hand". "It is too simple to test". "This case is different". Skipping the refactor step.

## Checklist before saying it is done

- Each new function or behavior has a test, seen failing for the right reason.
- Each test is minimal and uses real code where possible.
- The full suite passes with clean output; edge cases and error paths are covered.
- The refactor step was done, or "nothing to refactor" was stated.

If a box cannot be ticked, the cycle was skipped: go back.

## In ai-rules

Propose the test framework with a recommendation at project start and use the one the user validates (bats-core for shell, pytest for Python). The skill writes tests and code, never commits: when the cycle ends, write `.private/COMMIT_MESSAGE` and wait for the user's go (`core/commits.md`).
