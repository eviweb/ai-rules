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
