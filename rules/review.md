# Self-Review Checklist

Before proposing a commit or opening a PR, verify:

## Code
- [ ] No debug statements, commented-out code, or temporary hacks left in
- [ ] No hardcoded values that should be configurable or read from `VERSION`/env
- [ ] All TODOs either resolved or tracked as a new issue

## Tests
- [ ] All existing tests pass
- [ ] New behavior is covered by tests
- [ ] No tests skipped without justification

## Documentation
- [ ] `README.md` updated if behavior or usage changed
- [ ] `CHANGELOG.md` `[Unreleased]` section updated
- [ ] `VERSION` bumped if applicable

## Security
- [ ] No credentials, tokens, or secrets introduced
- [ ] Input validation in place for any new user-facing parameters
