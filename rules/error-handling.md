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
