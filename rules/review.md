# Review Guidelines

## Self-review checklist

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
- [ ] `VERSION` bumped if applicable

### Security
- [ ] No credentials, tokens, or secrets introduced
- [ ] `.env.example` updated if new environment variables were added
- [ ] Input validation in place for any new user-facing parameters

---

## Code review (as reviewer)

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
