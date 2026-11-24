# Testability
The system is designed so that its behaviour can be verified automatically and reliably.

- Inject dependencies rather than instantiating them inside functions — enables mocking and isolation
- Pure functions (no side effects) are easier to test; extract them from I/O-heavy code
- If a piece of code is hard to test, treat it as a design signal — restructure before writing workarounds
- Avoid global mutable state; prefer explicit parameter passing
- See `rules/tdd.md` and `rules/testing.md`

Red flags: untestable singletons, functions that require a running database to test business logic, tests that only work in CI, test coverage below 80%.
