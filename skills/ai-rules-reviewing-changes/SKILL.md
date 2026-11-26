---
name: ai-rules-reviewing-changes
description: "Use when about to propose a commit or open a pull request, or when reviewing a change or asked for a review: build the review package, self-review checklist (code, tests, docs, security), reviewer brief with graded findings, solo or team criteria."
metadata:
  derived-from: "superpowers/requesting-code-review @ 22f0b46"
  license-of-origin: MIT
---
# Reviewing changes

Review the change as it will be committed, not as you remember writing it. In ai-rules the agent never commits, so the review happens on the working tree, before `.private/COMMIT_MESSAGE` is written.

## 1. Build the review package

Run `scripts/review-package.sh` (in this skill's folder) from the repository. It writes one file with everything the review needs: the commits since the base, the staged, unstaged **and untracked** files, a stat summary and the diff with extended context. Untracked files are where self-reviews usually miss things: a new file never shows in `git diff`.

```bash
<skill-dir>/scripts/review-package.sh                 # base: merge base with main
<skill-dir>/scripts/review-package.sh --base v0.8.0   # another base
```

It prints the path of the package (`.private/reviews/`) and its size. Read the package, not the files one by one.

## 2. Self-review checklist

Before proposing a commit or opening a PR, verify:

### Code
- [ ] No debug statements, commented-out code, or temporary hacks left in
- [ ] No hardcoded values that should be configurable or read from `VERSION`/env
- [ ] All TODOs either resolved or tracked as a new issue
- [ ] `shellcheck` passes on all modified shell scripts

### Tests
- [ ] All existing tests pass
- [ ] New behavior is covered by tests
- [ ] No tests skipped without justification

### Documentation
- [ ] `README.md` updated if behavior or usage changed
- [ ] `CHANGELOG.md` `[Unreleased]` section updated
- [ ] `TODO.md` updated (tasks marked done, new tasks added)

### Security
- [ ] No credentials, tokens, or secrets introduced
- [ ] `.env.example` updated if new environment variables were added
- [ ] Input validation in place for any new user-facing parameters

## 3. Review against the intent

For a feature, a plan's final review or any change worth a second look, review the package against the spec or plan with the [reviewer brief](references/reviewer-brief.md): alignment with the spec, correctness and edge cases, design, tests, production readiness. Findings are graded **Blocking**, **Important** or **Minor** by their effect on a user, each with file and line, what is wrong, why it matters and the fix.

- A self-review by the author is weaker than a fresh reviewer: say so when you report it. The user may hand the package and the brief to another session or another agent; their findings come back through `ai-rules-receiving-code-review`.
- Blocking and important findings are fixed test-first before the commit is proposed. Minor findings are listed for the user, not fixed unasked.

## 4. Review criteria (as reviewer)

### Solo projects
When reviewing your own PR before merge (or asking Claude to review):

- [ ] The change solves the stated problem and nothing more
- [ ] No unintended side effects on existing behavior
- [ ] Logic is correct and edge cases are handled
- [ ] Names are explicit and intent is clear without needing comments
- [ ] No unnecessary complexity introduced

### Team projects
In addition to the solo checklist:

- [ ] The PR description clearly explains the why, not just the what
- [ ] The change is reviewable — not too large, not mixing unrelated concerns
- [ ] Conflicts with parallel work are identified and addressed
- [ ] API or interface changes are backwards-compatible or explicitly breaking
- [ ] Shared state, concurrency, or race conditions considered if applicable
- [ ] A second human reviewer has approved before merge
