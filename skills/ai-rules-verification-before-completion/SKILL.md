---
name: ai-rules-verification-before-completion
description: "Use when about to say work is done, fixed or passing, before writing a commit message, opening a pull request or moving to the next task: run the command that proves it and show its output first."
metadata:
  derived-from: "superpowers/verification-before-completion @ 22f0b46"
  license-of-origin: MIT
---
# Verification before completion

No success claim without evidence produced **in the current turn**. "Should work", "probably fixed" and "the agent said it passed" are not evidence. Confidence is not evidence either.

## Gate

1. Name the claim you are about to make ("tests pass", "bug fixed", "ready for review").
2. Find the command that would prove it, or disprove it.
3. Run it now, in full. A previous run, a partial run or a run before the last edit does not count.
4. Read the whole output and the exit code. Count the failures.
5. State the result with the proof: quote the decisive line (`301 passed`, exit code 0). If it fails, say what failed and the real status, not the hoped-for one.

Only then say it is done.

## What counts as proof

| Claim | Proof | Not enough |
|-------|-------|------------|
| Tests pass | Test run with 0 failures | An earlier run, "should pass" |
| Lint or type check clean | The linter run, 0 errors | A partial run, extrapolation |
| Build succeeds | The build command, exit 0 | Lint passing, logs looking fine |
| Bug fixed | The original symptom reproduced, then gone | Code changed, so assumed fixed |
| Regression test is real | Red, then green: it fails without the fix and passes with it | It passed once |
| Requirements met | A line-by-line check against the request or plan | Tests passing |
| Delegated work done | The diff (`git diff --stat`) read by you | The delegate's report |
| Config or infrastructure change | Syntax or dry-run check, then the service status (`nginx -t`, `haproxy -c`, `postfix check`, `--check`, `--dry-run`) | The file looks right |

## Red flags: stop and verify

- Words such as "should", "probably", "seems to", "I'm confident".
- Satisfaction before a result ("Done!", "Perfect!").
- About to propose a commit, push or open a PR without having run the checks.
- Reusing a result from before the last change, or checking only part of what the claim covers.
- "Just this once", or being tired of the task: neither changes what is true.

## In ai-rules

- Before writing `.private/COMMIT_MESSAGE`, run the project's tests and linters (for this repository `uv run pytest`, `uv run ruff check .`, `shellcheck`, `ai-rules verify`) and show the result.
- CI is evidence only when read: use `gh pr checks`, not memory of the last push.
- This skill only checks and reports. It never commits; after a verified result the commit gate of `core/commits.md` still applies.
