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
- Default log directory: `~/.local/state/<script-name>/logs/`
- Log filename: `<script-name>-YYYY-MM-DD.log`
- Disable with `--no-log`
- Override directory with `--log-dir <path>` or the env var `<SCRIPT_NAME>_LOG_DIR`
