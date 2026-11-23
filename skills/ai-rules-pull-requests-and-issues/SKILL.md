---
name: ai-rules-pull-requests-and-issues
description: "Use when writing or opening a pull request or an issue: title, description, linked issue, test checklist, labels, merge and branch cleanup rules."
---
# Pull Requests

## Title
- Follow Conventional Commits format: `type(scope): short description`

## Description
Every PR must include:
- **Summary** — what this PR does and why
- **Linked issue** — `Closes #n` (automatically closes the issue on merge). Mandatory in the strict profile; in the light profile, write `None` when no issue exists
- **Test checklist** — list of manual or automated verifications done

## Rules
- One PR = one topic — no bundling unrelated changes
- Do not merge without a green CI
- Merge with a merge commit to keep commit signatures (see `git.md`)
- Delete the branch after merge

# Issues

## Title
- Short and descriptive, written in English

## Description
Every issue must include:
- **Context** — why this matters, what triggered it
- **Expected behavior** — what should happen
- **Acceptance criteria** — explicit conditions that define the issue as resolved

## Labels
Apply at least one label:
- `bug` — something is broken
- `feat` — new feature or enhancement
- `chore` — maintenance, tooling, refactoring
- `docs` — documentation only

## Lifecycle
- Do not close an issue manually if a PR closes it automatically via `Closes #n`
- An issue should map to a single branch and a single PR
