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
- Default log directory: `~/.local/state/<script-name>/logs/`
- Log filename: `<script-name>-YYYY-MM-DD.log`
- Disable with `--no-log`
- Override directory with `--log-dir <path>` or the env var `<SCRIPT_NAME>_LOG_DIR`
