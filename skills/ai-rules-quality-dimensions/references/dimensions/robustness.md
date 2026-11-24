# Robustness
The system handles failures, invalid input, and unexpected conditions without crashing or corrupting state.

- Validate all inputs at system boundaries (user input, external APIs, file reads)
- Handle partial failures explicitly — never assume success
- Fail fast on unrecoverable errors; degrade gracefully on recoverable ones
- Use `set -euo pipefail` in shell, typed exceptions in Python, explicit error returns in Go
- See `rules/error-handling.md` for patterns

Red flags: silent failures, uncaught exceptions reaching users, missing input validation, bare `except:` or `|| true` without justification.
