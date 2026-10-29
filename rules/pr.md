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
