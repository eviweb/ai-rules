# Contributing to ai-rules

Thank you for considering a contribution. This document explains how to get
started and what to expect from the process.

## Ways to contribute

- **Report a bug** — open an issue using the bug report template
- **Propose a rule** — open a feature request describing the rule, its scope, and rationale
- **Add an agent integration** — open an issue first to discuss the approach
- **Improve documentation** — typos, clarity, missing examples

## Development setup

```bash
git clone git@github.com:eviweb/ai-rules.git
cd ai-rules
uv sync --extra dev
ln -sf ../../scripts/pre-commit .git/hooks/pre-commit
```

Run the test suite:

```bash
uv run pytest -v
```

Run the linter:

```bash
uv run ruff check src/ tests/
shellcheck scripts/pre-commit scripts/*.sh tests/run-tests.sh
```

## Workflow

1. Fork the repository
2. Create a branch: `git checkout -b feat/<short-description>`
3. Make your changes with tests
4. Ensure all tests pass and the linter is clean
5. Open a pull request against `main`

Branch naming follows the conventions in `rules/git.md`.
Commit messages follow Conventional Commits (`rules/commits.md`).

## Adding a rule file

- Place it in `rules/<name>.md`
- Reference it in `agents/claude/CLAUDE.md` under the appropriate section
- Run `ai-rules generate` to regenerate flat files for agents that need them
- Add tests if the rule affects CLI or installer behaviour

## Pull request checklist

- [ ] Tests pass (`uv run pytest -v`)
- [ ] Linter passes (`uv run ruff check`, `shellcheck`)
- [ ] `CHANGELOG.md` `[Unreleased]` section updated
- [ ] Flat files regenerated if rules changed (`ai-rules generate`)
- [ ] Flat files verified in sync (`ai-rules verify`)

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
All participants are expected to uphold it.
