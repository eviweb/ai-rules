# Global Rules

## Language & style
# Updated language rule
# Naming Conventions

## Shell scripts
- `UPPER_CASE` — constants, global variables, environment variables
- `lower_case` — local variables inside functions
- `_leading_underscore` — internal/private functions not meant to be called directly
- `lower_case` — public functions (descriptive verb-noun, e.g. `parse_arguments`, `check_dependencies`)
- Avoid abbreviations unless universally understood (e.g. `dir`, `tmp`, `cmd`)

## Files and directories
- `kebab-case` for script filenames (e.g. `install-forgejo.sh`)
- `UPPER_CASE` for top-level doc files (e.g. `README.md`, `CHANGELOG.md`)
- `lower_case` or `kebab-case` for directories

## Python
- `snake_case` — variables, functions, methods, module names
- `PascalCase` — classes, exceptions
- `UPPER_CASE` — module-level constants
- `_leading_underscore` — private attributes and methods
- `__dunder__` — reserved for Python special methods; never invent new dunder names
- Module filenames: `snake_case.py` (e.g. `config_loader.py`)
- Package directories: `snake_case` with `__init__.py`
- Avoid single-letter names except for loop counters (`i`, `j`) and well-established conventions (`x`, `y` for coordinates)

## JavaScript / TypeScript
- `camelCase` — variables, functions, method names
- `PascalCase` — classes, React components, type aliases, interfaces
- `UPPER_CASE` — module-level constants and enum values
- `_leading_underscore` — discouraged; prefer explicit `private` in TypeScript
- Filenames: `kebab-case.ts` for modules and utilities (e.g. `auth-service.ts`), `PascalCase.tsx` for React components (e.g. `UserCard.tsx`)
- Boolean variables: prefix with `is`, `has`, `can`, `should` (e.g. `isLoading`, `hasError`)
- Event handlers: prefix with `on` or `handle` (e.g. `onSubmit`, `handleClick`)

## Go
- `camelCase` — unexported (private) identifiers: variables, functions, methods, fields
- `PascalCase` — exported (public) identifiers: functions, types, methods, constants
- `UPPER_CASE` — avoid; Go idiom is `PascalCase` even for constants (e.g. `MaxRetries`)
- Short names for short-lived variables: `i`, `n`, `err`, `ok`, `v`, `k` are idiomatic
- Receiver names: short, consistent abbreviation of the type (e.g. `c` for `Client`, `s` for `Server`)
- Interface names: single-method interfaces use the method name + `-er` suffix (e.g. `Reader`, `Stringer`)
- Filenames: `snake_case.go` (e.g. `http_client.go`); test files: `snake_case_test.go`
- Packages: short, lowercase, single word — no underscores, no camelCase (e.g. `httputil`, `auth`)
- Avoid stutter: don't repeat the package name in exported identifiers (e.g. prefer `http.Client` over `http.HttpClient`)
# Editor Configuration

Every project must include an `.editorconfig` file at the root with at least the following settings:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.sh]
indent_style = space
indent_size = 2

[*.{js,ts,json,yml,yaml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

Adapt indentation rules to the language conventions of the project. Propose the `.editorconfig` at project start and wait for user validation.

## General principles
# General Coding Principles

## Analyze before coding
Always read and understand the relevant code before writing or modifying anything. Never edit a file that has not been read first. If the scope is unclear, ask before proceeding.

## Propose before implementing
For any non-trivial change, describe the intended approach and wait for explicit validation before writing code. This avoids costly back-and-forth on the wrong solution.

## Clarify before starting
If a request is ambiguous, incomplete, or could be interpreted in multiple ways, ask for clarification before writing any code. Starting on a wrong assumption wastes more time than a single clarifying question.

## Propose options before deciding
For any structuring choice (architecture, tooling, git strategy, framework, etc.), present the available options with their trade-offs and wait for explicit validation before proceeding. Never make a significant design decision autonomously.

## Prefer minimal diffs
Make the smallest change that correctly solves the problem. Do not touch code outside the scope of the request, even to fix style or improve readability.

## No refactoring without explicit request
Never restructure, rename, or reorganize existing code unless the user has explicitly asked for it. Refactoring mixed with feature changes makes review harder and increases risk.

## No speculative additions
Do not add features, options, abstractions, or error handling for hypothetical future needs. Implement only what is currently required.

## No dead code
Do not leave commented-out code, unused variables, or untracked TODOs. Either resolve them or open a tracked issue.

## Confirm before irreversible actions
Any action that is hard or impossible to undo (file deletion, branch deletion, `git reset --hard`, force-push, database drop, etc.) must be explicitly described to the user and confirmed before execution. Never perform destructive operations autonomously.

## Explicit naming
Names for functions, methods, classes, variables, and files must be as explicit as possible. Prefer clarity over brevity: a longer name that describes intent precisely is always better than a short name that requires context to understand.
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

## Development practices
# Test-Driven Development

> **TDD is mandatory.** There are no exceptions. Every feature, fix, or refactor must be driven by tests.

Always apply TDD. At the start of a project, propose one or more suitable test frameworks with a clear recommendation. Use the framework validated by the user throughout the project.

- Follow the Red-Green-Refactor cycle: write a failing test first, make it pass with minimal code, then refactor.
- Write tests before or alongside every new feature or fix. Never ship code without a corresponding test.
- Keep tests in a `tests/` directory with a dedicated runner script.
- For shell scripts: bats-core is the standard choice.
- Do not skip or defer tests — if a test is hard to write, it signals a design problem to fix first.
# Testing

Complements `rules/tdd.md` (which mandates TDD and the Red-Green-Refactor cycle). This file covers test structure, naming, coverage, and per-language conventions.

## Test pyramid

Write tests at the right level — don't over-invest in any single layer:

```
        /\
       /  \   E2E / integration (few, slow, high confidence)
      /----\
     /      \  Integration / contract (moderate)
    /--------\
   /          \ Unit (many, fast, isolated)
  /____________\
```

- **Unit tests**: test one function or class in isolation, no I/O, no network, no filesystem
- **Integration tests**: test the interaction between components (DB, HTTP, filesystem)
- **E2E tests**: test the full system from the user's perspective — keep these few and focused on critical paths

Rule: if a unit test requires mocking more than 2–3 dependencies, it is probably an integration test in disguise — restructure accordingly.

## Naming conventions

Test names must describe the scenario and expected outcome, not the implementation:

```
test_<unit>_<scenario>_<expected_outcome>
```

Examples:
- `test_parse_arguments_missing_flag_raises_error`
- `test_install_agent_dry_run_makes_no_changes`
- `test_generate_flat_file_overwrites_existing`

Avoid:
- `test_1`, `test_foo`, `testMethod` — meaningless
- `test_parse_arguments` alone — describes what, not when and what outcome

For bats (shell):
```bash
@test "install: dry run does not create symlink" { ... }
@test "generate: overwrites existing flat file" { ... }
```

## Test structure — Arrange / Act / Assert

Every test must follow the AAA pattern with a clear separation:

```python
def test_install_agent_backs_up_existing_file(repo_root, install_dir):
    # Arrange
    existing = install_dir / "entry.md"
    existing.write_text("old content")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])

    # Act
    actions = install_agent(repo_root, agent)

    # Assert
    assert any("BACKUP" in a for a in actions)
    assert (install_dir / "entry.md").is_symlink()
```

- One assertion per logical outcome — multiple `assert` calls are fine if they verify the same behaviour
- Never assert implementation details (internal calls, private state) — assert observable outcomes

## Coverage

- Minimum threshold: **80%** line coverage for application code
- Target **100%** for critical paths (auth, data validation, financial logic)
- Coverage is a floor, not a goal — 80% with meaningful tests beats 100% with trivial ones
- Exclude from coverage: migration files, generated code, `__main__` blocks, vendored code
- Configure thresholds in the project config and enforce in CI:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-fail-under=80"
```

## Test data and fixtures

- Use fixtures for shared setup — avoid duplicating setup code across tests
- Keep fixtures minimal: set up only what the test needs
- Prefer in-memory or temporary filesystem fixtures over real external systems in unit tests
- Name fixtures after the object they represent, not their role: `repo_root`, `agent`, not `setup`, `ctx`
- Never share mutable state between tests — each test must be fully independent

## Per-language conventions

### Python (pytest)
- One test file per module: `src/ai_rules/installer.py` → `tests/test_installer.py`
- Use `pytest.fixture` for setup; use `tmp_path` for temporary filesystem operations
- Parametrize repetitive cases with `@pytest.mark.parametrize`
- Mark slow or integration tests with `@pytest.mark.slow` and skip in fast runs

### Shell (bats-core)
- One `.bats` file per script under test
- Use `setup()` and `teardown()` for test isolation
- Use `bats-support` and `bats-assert` for readable assertions:
  ```bash
  load 'bats-support/load'
  load 'bats-assert/load'

  @test "script exits 0 on success" {
    run ./my-script.sh
    assert_success
  }
  ```

### JavaScript / TypeScript (Jest / Vitest)
- One test file per module: `src/auth.ts` → `src/auth.test.ts` or `tests/auth.test.ts`
- Use `describe` blocks to group related tests; `it` / `test` for individual cases
- Use `beforeEach` / `afterEach` for setup/teardown — never `beforeAll` for mutable state
- Mock external modules at the module boundary, not deep inside implementation code

### Go
- Test files alongside source: `config.go` → `config_test.go`
- Use table-driven tests for multiple input/output combinations:
  ```go
  tests := []struct {
      name  string
      input string
      want  string
  }{
      {"empty input", "", ""},
      {"valid value", "foo", "foo"},
  }
  for _, tt := range tests {
      t.Run(tt.name, func(t *testing.T) {
          got := process(tt.input)
          if got != tt.want {
              t.Errorf("got %q, want %q", got, tt.want)
          }
      })
  }
  ```
- Use `t.Helper()` in helper functions to get accurate failure line numbers
- Prefer `testify/assert` over raw `t.Error` for readability
# Security

- Never hardcode credentials, tokens, API keys, or passwords in source files
- Use environment variables or a secret manager for sensitive values
- Add secret files (`.env`, `*.key`, `*_token`, etc.) to `.gitignore` before the first commit
- Always version a `.env.example` file alongside `.env`: it lists all expected keys with empty or placeholder values, documents the required configuration without exposing secrets, and must be kept in sync with `.env` as new variables are added
- If a secret is accidentally committed: immediately inform the user, explain the risks (exposure in git history, potential misuse), attempt to remediate (e.g. `git filter-branch` or BFG, force-push if not yet public), and in all cases revoke/rotate the credential without delay

## File permissions
- Never create world-writable files
- Configuration files containing credentials: `600`
- Scripts that read sensitive configs: `700`

## Input validation
- Always validate and sanitize arguments before use in shell scripts to prevent command injection
- Reject or abort on unexpected/empty values for critical parameters

## External dependencies
- Check for required external commands at the top of every script before use:
  `command -v foo || { echo "foo is required" >&2; exit 1; }`

## Least privilege
- Scripts request only the permissions strictly necessary to function
- Never use `sudo` by default — only when explicitly required and documented

## Error handling
- Write error messages to `stderr` (`>&2`), never to `stdout`
- Use explicit and consistent exit codes (`exit 0` success, `exit 1` general error, higher values for specific cases)
- Avoid silencing errors with `|| true` unless the case is explicitly justified with a comment
# Dependencies

- Pin dependency versions explicitly — never use unpinned or wildcard versions in production
- Prefer actively maintained packages with a clear release history
- Run a security audit before each release (e.g. `npm audit`, `pip audit`, or equivalent)
- Keep dependencies up to date; review and update regularly
- Minimize the number of dependencies — prefer standard library or well-established tools over niche packages
- Document why each non-obvious dependency was chosen (in `README.md` or inline comment)
# Compatibility

## Shell
- Target **Bash 5+** by default; also support **zsh** unless the project is bash-only
- If POSIX `sh` compatibility is required, declare it explicitly at project start and avoid Bash-specific features (arrays, `[[`, `$(())`  with non-POSIX syntax, etc.)
- Declare the target shell in the shebang: `#!/usr/bin/env bash`
- Test interactive scripts on both bash and zsh when both are declared as targets

## Operating system
- Target **Ubuntu LTS** (current and previous release) and **Termux** (Android) by default
- Declare supported OS and versions in `README.md`
- If the script relies on OS-specific tools, document the assumption and add a compatibility check at startup
- Termux notes: no `sudo`, paths differ (`/data/data/com.termux/files/usr`), use `pkg` for packages

## XDG Base Directory compliance

All projects must follow the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/):

| Purpose        | Variable          | Default               | Use for                          |
|----------------|-------------------|-----------------------|----------------------------------|
| Configuration  | `XDG_CONFIG_HOME` | `~/.config`           | Config files                     |
| Data           | `XDG_DATA_HOME`   | `~/.local/share`      | Persistent application data      |
| State          | `XDG_STATE_HOME`  | `~/.local/state`      | Logs, history, runtime state     |
| Cache          | `XDG_CACHE_HOME`  | `~/.cache`            | Reproducible, expendable data    |
| Runtime        | `XDG_RUNTIME_DIR` | set by session manager| Sockets, PIDs, ephemeral files   |

Rules:
- Never hardcode `~/.config`, `~/.local`, etc. — always read the XDG variable with its default as fallback:
  ```bash
  CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/<app-name>"
  DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/<app-name>"
  STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/<app-name>"
  CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/<app-name>"
  ```
- Never write files directly to `$HOME` — use the appropriate XDG directory
- Document the XDG paths used by the application in `README.md`
- Termux exception: XDG variables may not be set by default; apply the same fallback pattern, which resolves correctly under Termux's `$HOME`

## Project structure & documentation
# Documentation

Every project must include the following files from the start:

- `README.md` — project description, usage, install instructions
- `CHANGELOG.md` — updated on every meaningful change
- `VERSION` — single line, semver (e.g. `1.0.0`), source of truth for version numbers
- `LICENSE.md` — ask the user to validate the license choice before creating it
- `TODO.md` — task tracker, structured by phases and themes (see below)

Keep all documentation up to date as the project evolves.

## TODO.md structure

`TODO.md` is the project's task tracker. It must be kept up to date alongside the code.

Structure:
```
# TODO

## Phase 1 — <name>
### <Theme>
- [ ] Task
- [x] Done task

## Phase 2 — <name>
...

---

## Future / Postponed
Items planned for a later phase, intentionally deferred.
- [ ] ...

## Deferred / Under Consideration
Ideas not yet committed to — may or may not happen.
- [ ] ...
```

Rules:
- Phases reflect the project's delivery roadmap; themes group related tasks within a phase
- "Future / Postponed" comes before "Deferred / Under Consideration": postponed items are more concrete (scoped but delayed), whereas under-consideration items are still exploratory
- Completed tasks (`[x]`) may be kept for traceability or removed — be consistent
- Add a separator (`---`) before the two trailing sections to visually distinguish backlog from active work

## Private directory

Every project must include a `.private/` directory and a `.gitignore` at the root.

Create `.private/` at project start — it holds local notes, draft messages, and
sensitive context that must never be committed.

The `.gitignore` must include at minimum:

```gitignore
# Private local directory
.private/

# Secrets and credentials
.env
.env.*
!.env.example
*.key
*.pem
*_token
*_secret

# OS artifacts
.DS_Store
Thumbs.db

# Editors
.idea/
.vscode/
*.swp
*.swo
*~

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
dist/
build/
*.egg-info/

# Node
node_modules/
npm-debug.log*

# Logs
*.log
logs/
```

Adapt to the project's language stack — add entries as needed, never remove the `.private/` entry.

## Community / open source (on user request)

When the user intends to share the project publicly, propose the following files and wait for explicit validation before creating each one:

- `CONTRIBUTING.md` — contribution guidelines (workflow, conventions, PR process)
- `CODE_OF_CONDUCT.md` — code of conduct (e.g. Contributor Covenant)
- `SECURITY.md` — vulnerability reporting policy
- `SUPPORT.md` — where to get help
- `.github/ISSUE_TEMPLATE/bug_report.md` — bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` — pull request template
- `AUTHORS.md` — list of contributors (optional, ask user)

The application/script must read its version from the `VERSION` file, not from a hardcoded constant.

**First commit of a new project:** `init: <short message>` with a detail block.
**Subsequent commits:** standard conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, etc.).
# Changelog

Follow the [Keep a Changelog](https://keepachangelog.com) format.

## Structure
- Always maintain an `[Unreleased]` section at the top for changes not yet released
- On release: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and add a new empty `[Unreleased]` section

## Sections (use only those that apply)
- `Added` — new features
- `Changed` — changes to existing functionality
- `Deprecated` — features to be removed in a future release
- `Removed` — removed features
- `Fixed` — bug fixes
- `Security` — vulnerability fixes

## Rules
- Every meaningful commit must have a corresponding entry in `[Unreleased]`
- Entries are written in English, in the imperative mood (e.g. "Add logging support")
- Do not list trivial changes (formatting, typos in comments, etc.)
# Semantic Versioning

All projects follow semver (`MAJOR.MINOR.PATCH`):

- **PATCH** — backwards-compatible bug fixes
- **MINOR** — new backwards-compatible functionality
- **MAJOR** — breaking changes

Bump the version in the `VERSION` file as part of the commit that introduces the change.

## Shell & CLI
# Shell Scripts

- Always enable strict mode at the top of every script: `set -euo pipefail`
- Run `shellcheck` on all scripts before proposing a commit
- Ensure scripts are executable: `chmod +x <script>`
- Use `local` for variables inside functions to avoid polluting global scope
- Use long flags by default for clarity; add the conventional short alias where standard convention exists (e.g. `-h|--help`, `-v|--verbose`, `-o|--output`)
- Prefer a structured invocation model when applicable: `script [options] command [options] subcommand [options] args` over a flat `script [options] args` — improves scalability and discoverability

## Cleanup & signal handling
- Always register a `trap` for cleanup when the script creates temporary files or acquires resources:
  ```bash
  cleanup() { rm -f "$tmp_file"; }
  trap cleanup EXIT INT TERM
  ```
- Handle `SIGINT` and `SIGTERM` gracefully — never leave temp files or partial state behind on interrupt
# CLI Projects

## Default options

Every CLI script must support the following options:

- `-h|--help` — display usage and exit
- `--debug` — enable trace mode (`set -x`) for troubleshooting
- `-V|--version` — display version and exit
- `-v|--verbose` — enable debug-level output
- `-q|--quiet` — suppress all terminal output
- `--dry-run` — simulate execution without making any changes
- `--no-color` — disable colored output
- `--no-log` — disable file logging
- `--log-dir <path>` — override the default log directory

## Invocation format

Unless the command is too simple to warrant it, prefer the following structured invocation model:

```
cli [global-options | namespaces | arguments(global-options, namespaces)]
    [contextual-options(namespaces) | commands | arguments(contextual-options, commands)]
    [contextual-options(commands) | subcommands | arguments(contextual-options, subcommands)]
```

- **Global options** apply regardless of the namespace or command (e.g. `--verbose`, `--dry-run`)
- **Namespaces** group related commands (e.g. `user`, `repo`, `config`)
- **Commands** are actions within a namespace (e.g. `create`, `delete`, `list`)
- **Subcommands** refine a command when needed (e.g. `list active`, `config set`)
- **Contextual options** apply only within the scope they are declared (namespace or command level)

Skip levels that are not relevant — a simple single-purpose script does not need namespaces or subcommands.

## Shell completion

Every CLI must provide shell completion. This is not optional — completion is part of the user experience contract of any CLI tool.

- Support at minimum: **bash**, **zsh**, **fish**
- Expose completion via `--install-completion` (installs for the current shell) and `--show-completion` (prints the script for manual setup)
- When using **typer**: completion is built-in, no extra code required
- When using **argparse** or a custom shell CLI: implement completion manually or via a dedicated library (e.g. `argcomplete` for Python, `bash-completion` for shell scripts)
- Document the completion setup in `README.md`

## Debug mode
- `--debug` activates `set -x` to trace execution
- Debug output goes to `stderr` only
- Never commit code with `set -x` hardcoded or debug traces left in — use the `--debug` flag exclusively

## Colored terminal output

- Log levels and their colors: `INFO` (white), `WARN` (yellow), `ERROR` (red), `DEBUG` (cyan)
- Apply colors only when output is a TTY (`[ -t 1 ]`) and `NO_COLOR` is not set (see https://no-color.org)
- Log format: `[YYYY-MM-DD HH:MM:SS] [LEVEL] message`

## File logging

- Enabled by default alongside terminal output (without ANSI color codes)
- Same format as terminal output
- Default log directory: `${XDG_STATE_HOME:-$HOME/.local/state}/<script-name>/logs/`
- Log filename: `<script-name>-YYYY-MM-DD.log`
- Disable with `--no-log`
- Override directory with `--log-dir <path>` or the env var `<SCRIPT_NAME>_LOG_DIR`
# Logging (application-level)

Applies to non-CLI projects (libraries, services, daemons, APIs). For CLI-specific logging see `rules/cli.md`.

## Log levels

Use the following levels, in ascending severity order:

| Level | Use for |
|-------|---------|
| `DEBUG` | Detailed diagnostic info, off in production |
| `INFO` | Normal operational events (startup, request received, job done) |
| `WARN` | Unexpected but recoverable situation — something worth investigating |
| `ERROR` | Failure that affects an operation but not the whole process |
| `FATAL` / `CRITICAL` | Unrecoverable failure — process must stop |

Rules:
- Never use `print()` or equivalent for logging — always go through the logging system
- `DEBUG` must be disabled by default and enabled via config or env var
- Do not log sensitive data (tokens, passwords, PII) at any level

## Structured logging

Prefer structured (machine-readable) logs over plain text in any service that may be aggregated or monitored:

- Use JSON format for services and daemons
- Each log entry must include at minimum: `timestamp`, `level`, `message`
- Add `service`, `version`, and `trace_id` / `request_id` when available
- Example:
  ```json
  {"timestamp": "2026-04-20T10:00:00Z", "level": "INFO", "service": "api", "version": "1.2.0", "message": "Request handled", "request_id": "abc123", "duration_ms": 42}
  ```

## Log output

- Write to `stderr` by default — never pollute `stdout` with log lines
- In services: also write to a log file or a log aggregator (see below)
- Log file location follows XDG: `${XDG_STATE_HOME:-$HOME/.local/state}/<app-name>/logs/`

## Log aggregation

When the project runs in a multi-instance or production environment, document the aggregation strategy in `README.md`:

- **Local / single-node**: rotating file logs (e.g. `logrotate`, `logging.handlers.RotatingFileHandler`)
- **Containerised**: write to `stdout`/`stderr` and let the container runtime collect them
- **Distributed**: ship logs to a centralised system (e.g. Loki, ELK, CloudWatch) — document the sink and the expected format

## Per-language guidance

### Python
- Use the standard `logging` module — never `print()`
- Configure via `logging.basicConfig()` or a `logging.config.dictConfig()` file
- Library code: attach a `NullHandler` only — never configure handlers in library code
  ```python
  import logging
  logging.getLogger(__name__).addHandler(logging.NullHandler())
  ```
- Application code: configure at entry point, propagate to all modules

### Shell scripts
- See `rules/cli.md` for CLI-specific log format and file logging conventions
- For non-interactive scripts (cron, daemons): redirect output to a log file and use `logger` for syslog integration

### Node.js / TypeScript
- Use a structured logger (e.g. `pino`, `winston`) — never `console.log()` in production code
- Configure log level via `LOG_LEVEL` env var
# Error Handling

## General principles

- Fail explicitly — never silently swallow errors
- Error messages go to `stderr`, never `stdout`
- Every error must include enough context to diagnose the cause without reading source code (what failed, why, what to do)
- Distinguish between user errors (wrong input → recoverable) and system errors (unexpected state → may require abort)

## Exit codes (shell / CLI)

Use consistent, documented exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (unspecified) |
| `2` | Misuse — bad arguments, missing required input |
| `3`–`125` | Application-specific errors — document them in the script header or `--help` |
| `126` | Command found but not executable |
| `127` | Command not found |
| `128+N` | Terminated by signal N (e.g. `130` = SIGINT) |

Rules:
- Never use `exit 0` to mask a failure
- Avoid `|| true` unless the case is explicitly justified with a comment
- Define and document custom exit codes at the top of the script

## Error message format

Write messages that help the user act, not just observe:

```
Error: <what failed>: <reason>
```

Examples:
```
Error: config file not found: /home/user/.config/app/config.toml
Error: required dependency missing: jq (install with: apt install jq)
Error: invalid argument: --timeout must be a positive integer, got '-5'
```

Rules:
- Capitalise the first word, no trailing period
- Name the exact resource or value that caused the failure
- Include a remediation hint when the fix is known and unambiguous
- Never expose internal stack traces to end users — log them at DEBUG level

## Shell

- `set -euo pipefail` catches most silent failures — always enable at the top of every script
- Wrap critical commands with explicit error messages:
  ```bash
  foo_output=$(some_command) || { echo "Error: some_command failed" >&2; exit 1; }
  ```
- Check for required commands before use:
  ```bash
  command -v jq >/dev/null 2>&1 || { echo "Error: jq is required (apt install jq)" >&2; exit 1; }
  ```
- Use `trap` to clean up on unexpected exit (see `rules/shell.md`)

## Python

- Use specific exception types — never `except Exception` or bare `except:` for flow control
- Catch exceptions at the boundary where you can add context, not deep inside library code:
  ```python
  try:
      config = load_config(path)
  except FileNotFoundError:
      raise SystemExit(f"Error: config file not found: {path}")
  ```
- Re-raise with context using `raise ... from`:
  ```python
  except OSError as exc:
      raise RuntimeError(f"Failed to write {path}") from exc
  ```
- Use `logging.exception()` to log the full traceback at ERROR level before exiting
- CLI entry points: catch top-level exceptions and exit with a clean message + non-zero code; never let a raw traceback reach the user

## Go

- Return errors explicitly — never panic for expected failure conditions
- Wrap errors with context at each layer using `fmt.Errorf("doing X: %w", err)`:
  ```go
  if err := db.Connect(dsn); err != nil {
      return fmt.Errorf("connecting to database: %w", err)
  }
  ```
- Use `errors.Is` / `errors.As` for sentinel checks — never compare error strings
- Panic only for truly unrecoverable programmer errors (invariant violations), not for runtime conditions
- At the top level (main), log the error and exit with a non-zero code:
  ```go
  if err := run(); err != nil {
      log.Fatalf("Error: %v", err)
  }
  ```

## JavaScript / TypeScript

- Use typed errors — extend `Error` with a custom class for domain-specific failures:
  ```typescript
  class ConfigError extends Error {
    constructor(message: string) {
      super(message);
      this.name = "ConfigError";
    }
  }
  ```
- Always handle Promise rejections — never leave unhandled `.catch()` absent on async chains
- In async/await code, wrap at the boundary that owns the recovery decision:
  ```typescript
  try {
      await loadConfig(path);
  } catch (err) {
      if (err instanceof ConfigError) { /* handle */ }
      throw err; // re-throw unexpected errors
  }
  ```
- Never use `console.error` in library code — throw and let the caller decide
- Express API endpoints: always use an error-handling middleware as the last middleware; never send raw error objects to the client
# API Design

Applies to HTTP/REST APIs. For GraphQL or gRPC, adapt the principles but follow the conventions of the respective ecosystem.

## URL structure

- Use `kebab-case` for path segments: `/user-profiles`, not `/userProfiles` or `/user_profiles`
- Use nouns for resources, never verbs: `/orders`, not `/getOrders`
- Nest resources only when the relationship is ownership and the nesting depth is ≤ 2:
  `/users/{id}/orders` — acceptable
  `/users/{id}/orders/{id}/items/{id}/details` — too deep, flatten it
- Use plural nouns for collections: `/articles`, `/comments`
- Resource identifiers in path: `{id}` for primary key, use UUIDs over sequential integers in public APIs

## HTTP methods

| Method | Use for | Idempotent | Body |
|--------|---------|-----------|------|
| `GET` | Read resource or collection | yes | no |
| `POST` | Create resource, trigger action | no | yes |
| `PUT` | Replace resource entirely | yes | yes |
| `PATCH` | Partial update | no | yes |
| `DELETE` | Remove resource | yes | no |

- Never use `GET` for operations with side effects
- Prefer `PATCH` over `PUT` for partial updates — `PUT` requires sending the full representation

## HTTP status codes

Return the most specific applicable code. Common codes:

| Code | Meaning | When to use |
|------|---------|-------------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST that created a resource |
| `204` | No Content | Successful DELETE or action with no response body |
| `400` | Bad Request | Malformed request, validation failure |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | State conflict (duplicate, version mismatch) |
| `422` | Unprocessable Entity | Valid syntax but semantic validation failed |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server-side failure |
| `503` | Service Unavailable | Downstream dependency unavailable |

- Never return `200` with an error payload — use the correct error code
- `404` vs `403`: if revealing existence is a security concern, return `404` consistently

## Versioning

- Version in the URL path: `/v1/`, `/v2/` — explicit, cacheable, easy to route
- Bump the major version only for breaking changes; additive changes (new fields, new endpoints) are non-breaking
- Maintain at least one previous major version during a deprecation window
- Announce deprecation via a `Deprecation` response header and documentation

## Request / response format

- Default content type: `application/json`
- Use `camelCase` for JSON field names
- Always return a consistent envelope for collections:
  ```json
  {
    "data": [...],
    "meta": {
      "total": 100,
      "page": 1,
      "per_page": 20
    }
  }
  ```
- For single resources, return the object directly (no wrapper):
  ```json
  { "id": "abc", "name": "Alice", "createdAt": "2026-04-20T10:00:00Z" }
  ```
- Use ISO 8601 for all timestamps: `2026-04-20T10:00:00Z`
- Use strings for large integers (> 2^53) to avoid precision loss in JavaScript clients

## Error response format

Return a consistent error body on all 4xx and 5xx responses:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "issue": "must be a valid email address" }
    ]
  }
}
```

- `code`: machine-readable uppercase string — stable across versions
- `message`: human-readable summary
- `details`: optional array for field-level or multi-error cases
- Never expose stack traces, internal paths, or database errors in the response body — log them server-side

## Pagination

Use cursor-based pagination for large or frequently updated collections; use offset pagination only for small, stable datasets.

### Cursor-based (preferred)
```json
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJpZCI6MTIzfQ==",
    "has_more": true
  }
}
```

### Offset-based
```json
{
  "data": [...],
  "meta": {
    "total": 500,
    "page": 3,
    "per_page": 20
  }
}
```

- Default page size: 20; maximum: 100 — enforce server-side, never trust client values
- Document pagination strategy in the API reference

## Authentication

- Use `Authorization: Bearer <token>` for token-based auth (JWT, opaque tokens)
- Never pass credentials in query parameters — they appear in server logs and browser history
- Use HTTPS everywhere — never serve an API over plain HTTP
- Document the auth scheme in `README.md` or a dedicated API reference

## Rate limiting

- Always rate-limit public and authenticated endpoints
- Return `429 Too Many Requests` with `Retry-After` header when limit is exceeded:
  ```
  HTTP/1.1 429 Too Many Requests
  Retry-After: 30
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1745145600
  ```
- Document rate limits in the API reference

## Documentation

- Every API must have an OpenAPI (Swagger) spec — generate it from code annotations when possible
- Keep the spec versioned alongside the code in the repository
- Document all endpoints, request/response schemas, error codes, and auth requirements

## Git & collaboration
# Git Workflow

## Permanent branches

| Branch | Role |
|---|---|
| `main` | Stable, always-deployable code. Protected — no direct commits. |
| `develop` | Continuous integration of features before release (optional — use only for projects with a long release cycle). |

For simple projects: `main` alone is sufficient, without `develop`.

## Working branches (short-lived)

Created from `main` (or `develop` if present), deleted after merge.

| Prefix | Usage | Example |
|---|---|---|
| `feat/` | New feature | `feat/add-auth` |
| `fix/` | Bug fix | `fix/login-crash` |
| `chore/` | Maintenance, tooling, dependencies | `chore/update-deps` |
| `docs/` | Documentation only | `docs/api-reference` |
| `test/` | Tests only | `test/add-bats-suite` |
| `release/` | Release preparation (version bump, changelog) | `release/1.2.0` |
| `hotfix/` | Urgent fix applied directly on top of `main` | `hotfix/critical-null-ptr` |

## Synchronization strategy: rebase

When `main` has moved ahead of a working branch, synchronize with:

```bash
git rebase main
```

- Produces a linear, readable history
- Resolves conflicts commit by commit
- **Never rebase a branch that has already been pushed and shared** — this rewrites history and will break other contributors. Use `git push --force-with-lease` only when the branch is personal and you are certain no one else is working on it.

## Merge strategy: squash merge

When merging a PR into `main`, use squash merge:

- One commit per feature/fix on `main` — clean, bisect-friendly history
- Eliminates noise commits (`wip`, `fix typo`, `try again`)
- Rollback is simple: one commit to revert
- **The squash commit message must be written carefully** — do not use the auto-generated message. Write a proper conventional commit message that summarizes the intent of the entire branch.

Exception: hotfixes that consist of a single meaningful commit can be merged directly without squashing.

## Workflow by case

**Feature / fix / chore**
1. Create branch from `main`: `git checkout -b feat/<description>`
2. Develop with conventional commits
3. Rebase on `main` if it has diverged: `git rebase main`
4. Open a PR toward `main`
5. CI green + review → squash merge with a clean commit message
6. Delete the branch

**Hotfix (critical production bug)**
1. Create `hotfix/<description>` from `main`
2. Fix and test
3. Open a PR toward `main` — fast merge
4. Delete the branch

**Release**
1. Create `release/X.Y.Z` from `main`
2. Bump `VERSION`, update `CHANGELOG.md`
3. Open a PR toward `main` → merge → tag `X.Y.Z`
4. Delete the branch

## General rules

- One branch = one topic = one PR
- Keep branches short-lived — rebase regularly to avoid large divergence
- Never merge directly to `main` without a PR
- Branch names must be self-explanatory without additional context

## Deleting merged branches

After a PR is merged on GitHub, always use `git branch -D` (force delete) rather than `git branch -d`:

```bash
# Confirm the PR is merged first
gh pr view <number> --json state -q .state

# Then force-delete the local branch
git branch -D <branch>
```

`git branch -d` checks that the branch SHA exists in the current HEAD history.
When GitHub uses squash merge or rebase merge, commit SHAs are rewritten — the
local branch will never be recognized as merged, and `-d` will always fail.

## Merge conflicts

- Always analyze both sides of a conflict before resolving — never blindly apply `--ours` or `--theirs`
- Prefer manual resolution that preserves the intent of both changes when possible
- If the correct resolution is ambiguous, stop and ask the user before proceeding
# Git Commits

## Format
- Follow Conventional Commits: `type(scope): message`
- Never include emojis in commit messages — the global `commit-msg` hook adds them automatically via `insert-icon`
- Always use `git commit -s` to append a `Signed-off-by` trailer (DCO compliance + GPG signing)
- **Prefer detailed commit messages** — whenever a commit touches multiple files or introduces non-obvious changes, add a body listing the key changes. A one-liner is acceptable only for genuinely trivial commits (e.g. typo fix, single-line change). When in doubt, add detail:

  ```
  type(scope): short summary

  - Change A: why it was needed
  - Change B: what it replaces or fixes
  - Change C: any non-obvious consequence
  ```

## Hook behavior
- The global `commit-msg` hook runs `cog verify` then `insert-icon`
- Check that `LEGACY_COMMIT_MESSAGE` is `0` before committing to ensure the hook runs
- Set `git config hook.legacyCommitMessage true` in two cases (bypasses the hook entirely — no icon added):
  1. The message intentionally does NOT follow Conventional Commits
  2. The existing commit history uses the old format (plain message without `type(scope):`) — use legacy mode to maintain consistency within that repository

## Claude Code commit workflow
- **Never commit autonomously.** Commits must be explicitly requested by the user AND confirmed before execution.
- After every set of modifications, always propose a commit message covering **all modified files** — code, tests, and documentation included.
- Before proposing a commit to the user, write the message to `.private/COMMIT_MESSAGE` (create the file if absent, overwrite if present).
- Wait for the user's explicit go-ahead before running any `git commit` command.
- **When multiple commits are planned in sequence:** stop after each commit and wait for the user's explicit instruction to continue. Do not chain commits autonomously.
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
# Pull Requests

## Title
- Follow Conventional Commits format: `type(scope): short description`

## Description
Every PR must include:
- **Summary** — what this PR does and why
- **Linked issue** — `Closes #n` (automatically closes the issue on merge)
- **Test checklist** — list of manual or automated verifications done

## Rules
- One PR = one topic — no bundling unrelated changes
- Do not merge without a green CI
- Delete the branch after merge
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

## CI/CD & release
# Continuous Integration

## Setup
- Workflow files:
  - Forgejo: `.forgejo/workflows/`
  - GitHub: `.github/workflows/`
- Propose the CI structure at project start and wait for user validation before creating it
- Add a CI status badge to `README.md` once the workflow is in place

## Triggers
- Run on `push` and `pull_request`

## Jobs
- **lint** — run `shellcheck` on all shell scripts
- **test** — run the bats-core test suite
- **build** — run if the project produces build artifacts

## Rules
- Fail fast on error
- Never hardcode secrets in workflow files — use platform secrets (Forgejo variables/secrets or GitHub Actions secrets)

## Job timeouts

Set explicit timeouts on every job to prevent runaway builds from consuming minutes/credits:

| Job type | Recommended timeout |
|----------|-------------------|
| lint | 5 min |
| unit tests | 15 min |
| integration tests | 30 min |
| build | 20 min |
| deploy | 15 min |

```yaml
jobs:
  test:
    timeout-minutes: 15
```

Default to the shortest reasonable value — increase only when a job consistently needs more.

## Caching strategies

Cache dependency installs to avoid re-downloading on every run. Always key on the lockfile so the cache is invalidated when dependencies change.

### Python (uv / pip)
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
    restore-keys: uv-${{ runner.os }}-
```

### Node.js (npm)
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
    restore-keys: npm-${{ runner.os }}-
```

### Node.js (pnpm)
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.local/share/pnpm/store
    key: pnpm-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
    restore-keys: pnpm-${{ runner.os }}-
```

### Rust (cargo)
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target/
    key: cargo-${{ runner.os }}-${{ hashFiles('Cargo.lock') }}
    restore-keys: cargo-${{ runner.os }}-
```

Rules:
- Always use a lockfile as the cache key hash — never hash `package.json` or `pyproject.toml` alone
- Add a `restore-keys` fallback so partial cache hits still save time
- Never cache build outputs that contain secrets or environment-specific paths

## Artifact retention

Attach artifacts only when they provide diagnostic or release value. Set short retention for ephemeral artifacts.

| Artifact type | Retention |
|---------------|-----------|
| Test reports / coverage | 7 days |
| Build artifacts (non-release) | 7 days |
| Release artifacts | 90 days (or keep via platform release) |

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-report
    path: reports/
    retention-days: 7
```

- Do not upload artifacts on every push — scope uploads to relevant branches (`main`, release branches) or failure conditions
- Always name artifacts explicitly — avoid generic names like `output` or `build`
# Release Workflow

## Pre-release checklist
- Ensure all tests pass and CI is green
- Bump the `VERSION` file (follow semver rules from `versioning.md`)
- Update `CHANGELOG.md`: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and add a new empty `[Unreleased]` section
- Verify the tag does not already exist

## Release commit
- Commit message: `chore(release): bump version to X.Y.Z`
- Wait for explicit user validation before committing and tagging

## Release message
- Before any release action, draft a detailed release message covering: summary of changes, breaking changes (if any), migration steps (if any), notable fixes
- Write the draft to `.private/RELEASE_MESSAGE` (create if absent, overwrite if present)
- Present it to the user for review before using it in the platform release

## Tagging
- Tag format: `X.Y.Z` (no `v` prefix), must match the content of `VERSION`
- Before tagging, write the tag message to `.private/TAGGING_MESSAGE` (create if absent, overwrite if present)
- Push the tag only after user confirmation:
  ```bash
  git tag X.Y.Z
  git push origin X.Y.Z
  ```

## Platform release

Create the platform release **after** the tag has been pushed. Use the corresponding `CHANGELOG.md` section as release notes.

### GitHub

```bash
gh release create X.Y.Z \
  --title "X.Y.Z" \
  --notes-file <(scripts/extract-changelog.sh X.Y.Z) \
  --latest
```

### Forgejo

Using the `tea` CLI (install: `tea` from https://gitea.com/gitea/tea):

```bash
tea releases create \
  --tag X.Y.Z \
  --title "X.Y.Z" \
  --note "$(scripts/extract-changelog.sh X.Y.Z)"
```

Alternatively, via the Forgejo REST API:

```bash
curl -s -X POST "https://<forgejo-host>/api/v1/repos/<owner>/<repo>/releases" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tag_name": "X.Y.Z",
    "name": "X.Y.Z",
    "body": "<release notes>",
    "draft": false,
    "prerelease": false
  }'
```

## Artifacts
- Package and attach release artifacts if applicable (e.g. `.tar.gz` archive)
- GitHub: add artifact paths as additional arguments to `gh release create`
- Forgejo: use `tea releases assets create` or the API endpoint `POST /repos/{owner}/{repo}/releases/{id}/assets`
