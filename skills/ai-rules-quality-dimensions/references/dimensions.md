# Project Quality Dimensions

Every project must be designed with all applicable dimensions below in mind from the start — not retrofitted after the fact. At project kickoff, identify which dimensions are critical for the use case and document any conscious trade-offs made.

---

## Robustness
The system handles failures, invalid input, and unexpected conditions without crashing or corrupting state.

- Validate all inputs at system boundaries (user input, external APIs, file reads)
- Handle partial failures explicitly — never assume success
- Fail fast on unrecoverable errors; degrade gracefully on recoverable ones
- Use `set -euo pipefail` in shell, typed exceptions in Python, explicit error returns in Go
- See `rules/error-handling.md` for patterns

Red flags: silent failures, uncaught exceptions reaching users, missing input validation, bare `except:` or `|| true` without justification.

---

## Security
The system protects its data, users, and infrastructure from misuse and attack.

- Never hardcode credentials or secrets — use env vars or a secret manager
- Validate and sanitise all external input to prevent injection
- Apply least privilege: request only the permissions strictly needed
- Keep dependencies up to date and audit them regularly
- See `rules/security.md` for patterns

Red flags: secrets in source, world-writable files, unvalidated input passed to shell commands or SQL, overly broad permissions.

---

## Performance
The system responds within acceptable time and resource bounds under expected load.

- Define performance targets at project start (response time, throughput, memory budget)
- Measure before optimising — never optimise based on intuition alone
- Avoid unnecessary I/O in hot paths; prefer lazy loading over eager loading
- Cache results that are expensive to compute and stable enough to cache safely
- Profile under realistic load, not synthetic microbenchmarks alone

Red flags: N+1 queries, unbounded loops over external data, synchronous blocking in async contexts, caches with no invalidation strategy.

---

## Extensibility
The system can accommodate new requirements without requiring rewrites of existing components.

- Separate concerns: each module has one reason to change
- Depend on abstractions, not concrete implementations — inject dependencies
- Avoid hardcoded assumptions about the number of items, types, or destinations (e.g. hardcoding agent names instead of reading from config)
- Design for the current requirements; leave extension points only where growth is certain
- Document the intended extension points in `README.md`

Red flags: God classes, feature flags proliferating across the codebase, copy-paste instead of abstraction, tight coupling between unrelated modules.

---

## User-friendliness
The system is easy to use correctly and hard to use incorrectly.

- Error messages tell the user what went wrong, why, and how to fix it
- Defaults are sensible — the common case requires no configuration
- `--help` is complete, accurate, and includes examples
- Destructive operations require explicit confirmation or a `--dry-run` preview
- Output is readable: use colour when appropriate, respect `NO_COLOR`, format tables clearly

Red flags: cryptic error codes without explanation, no `--help`, silent success for operations that changed nothing, irreversible actions without confirmation.

---

## Maintainability
The codebase can be understood, modified, and extended by anyone familiar with the language — including yourself six months from now.

- Names are explicit and describe intent — no abbreviations, no single-letter variables outside loops
- Functions do one thing; if a function needs a comment to explain what it does, rename it or split it
- No dead code, no commented-out blocks, no untracked TODOs
- Complexity is documented where unavoidable (non-obvious invariant, external constraint, workaround for a known bug)
- See `rules/principles.md` and `rules/naming.md`

Red flags: functions > 50 lines, deeply nested conditions, magic numbers, copy-paste logic, code that only the original author can explain.

---

## Observability
The system exposes enough information to understand its behaviour in production without modifying or redeploying it.

- Log meaningful events at the right level (see `rules/logging.md`)
- Expose a health check endpoint for services (`/health` or `/healthz`)
- Emit metrics for key operations: request count, error rate, latency, queue depth
- Use structured logs with a consistent schema so they can be queried
- In distributed systems: propagate a `trace_id` / `request_id` across service calls

Red flags: no logs in production paths, logs that say "error occurred" without context, no way to check if the service is healthy, metrics only on happy paths.

---

## Testability
The system is designed so that its behaviour can be verified automatically and reliably.

- Inject dependencies rather than instantiating them inside functions — enables mocking and isolation
- Pure functions (no side effects) are easier to test; extract them from I/O-heavy code
- If a piece of code is hard to test, treat it as a design signal — restructure before writing workarounds
- Avoid global mutable state; prefer explicit parameter passing
- See `rules/tdd.md` and `rules/testing.md`

Red flags: untestable singletons, functions that require a running database to test business logic, tests that only work in CI, test coverage below 80%.

---

## Portability
The system works correctly across all declared target environments without environment-specific hacks.

- Follow XDG Base Directory spec for file locations (see `rules/compatibility.md`)
- Never hardcode absolute paths — use relative paths or configurable roots
- Test on all declared platforms (Ubuntu LTS, Termux) before release
- Document environment requirements and compatibility constraints in `README.md`

Red flags: hardcoded `/home/username/`, Linux-only syscalls without a fallback, dependencies that don't exist on Termux, undocumented OS assumptions.

---

## Auditability
Actions taken by the system are traceable — who did what, when, and with what result.

- Log all state-changing operations with enough context to reconstruct the sequence of events
- Include actor identity (user, service, API key ID) in log entries for authenticated systems
- Never log sensitive data (passwords, tokens, PII) — log identifiers, not values
- Retain audit logs separately from application logs, with a longer retention period
- For CLIs: log commands and their outcomes to the state log file

Red flags: no record of what changed and when, logs that are overwritten or rotated too aggressively, audit and debug logs mixed in the same stream.

---

## Privacy & data minimisation
The system collects, stores, and processes only the data strictly necessary for its purpose.

- Identify personal data at design time — document what is collected and why
- Apply retention limits: delete or anonymise data when it is no longer needed
- Do not log PII (names, emails, IP addresses, user identifiers) unless explicitly required and documented
- Provide a way to delete user data on request (right to erasure)
- Apply data minimisation at every layer: API responses, database queries, log entries

Red flags: logging full request bodies that may contain PII, no data retention policy, storing data "just in case", third-party analytics that collect more than needed.

---

## Resilience
The system continues to function — possibly in a degraded mode — when a dependency or component fails.

- Identify single points of failure at design time and document mitigation strategies
- Implement timeouts on all external calls — never wait indefinitely
- Use retries with exponential backoff for transient failures; set a maximum retry budget
- Design for partial availability: if a non-critical dependency is down, degrade gracefully rather than failing entirely
- Test failure scenarios explicitly (dependency unavailable, timeout, malformed response)

Red flags: no timeouts on HTTP calls, infinite retry loops, cascading failures when one service goes down, no graceful degradation path documented.
