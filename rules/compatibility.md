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
