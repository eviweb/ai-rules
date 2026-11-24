---
name: ai-rules-systematic-debugging
description: "Use when facing a bug, a failing test, a build or CI failure or unexpected behavior, before proposing or applying a fix: find the root cause first, then test one hypothesis at a time."
metadata:
  derived-from: "superpowers/systematic-debugging @ 22f0b46"
  license-of-origin: MIT
---
# Systematic debugging

Find the root cause before changing anything. A fix that hides the symptom is a failure, not a shortcut, and guessing is slower than looking. This applies to bugs, failing tests, build and CI failures, performance problems and integration issues, above all under time pressure or when a quick fix looks obvious.

No fix is proposed before phase 1 is finished.

## Phase 1: investigate

1. **Read the evidence**: the whole error message, the full stack trace, the exit code, the logs around the failure. Do not skim.
2. **Reproduce** it reliably, with the smallest command that fails. If it does not reproduce, collect more data (logs, inputs, environment); do not guess.
3. **Check what changed**: `git diff`, recent commits, dependency or config updates, environment differences.
4. **Instrument component boundaries** when the failure crosses several parts (CI to build to deploy, client to proxy to service to database): record what enters and leaves each part, once, and see where the data first goes wrong. Then investigate that part only. Examples for DNS, proxies, containers and services: [infrastructure examples](references/infra-examples.md).
5. **Trace backward** from the bad value to where it was produced, and fix it there, not where it surfaced.

## Phase 2: compare

- Find similar code or a configuration that works, and read it completely.
- List every difference with the broken one, however small, and the assumptions each side makes.

## Phase 3: hypothesize and test

1. Write one hypothesis: "the cause is X because Y".
2. Test it with the smallest possible change, changing **one variable at a time**.
3. If it is wrong, drop it and form another from what you just learned. Never stack changes on top of a failed one. If you do not understand something, say so and look it up or ask.

## Phase 4: fix

1. Write a failing test that reproduces the bug first (see `ai-rules-test-driven-development`); for configuration or infrastructure, keep the failing command as the reproduction.
2. Make one change that addresses the root cause. No refactoring, no "while I'm here" edits.
3. Prove it with `ai-rules-verification-before-completion`: the reproduction now passes and nothing else broke.
4. Put the cause, not only the effect, in the commit message body.

## When fixes keep failing

- Fewer than three failed fixes: go back to phase 1 with what you learned.
- **Three failed fixes: stop.** Each fix revealing a new problem elsewhere, or needing a large refactoring, points at the design, not at a bad hypothesis. Describe what you found, present the options with their trade-offs, and wait for the user's decision before a fourth attempt (`core/principles.md`).

## When no cause is found

If the cause is external, intermittent or environmental, say so with the evidence, add the right handling (timeout, retry, explicit error message, logging) and document it. Most "no root cause" cases are an investigation that stopped too early: check again before concluding.

## Red flags: back to phase 1

"Quick fix now, investigate later", "just try changing X", several changes at once, skipping the reproduction test, "it's probably X", "one more attempt" after two failures, a proposed fix before any data flow was traced.

## In ai-rules

This skill investigates and proposes. It changes nothing without the user's agreement on the approach, and it never commits; the commit gate of `core/commits.md` applies to the fix.
