# Compatibility

## Shell
- Target **Bash 5+** by default
- If POSIX `sh` compatibility is required, declare it explicitly at project start and avoid Bash-specific features (arrays, `[[`, `$(())`  with non-POSIX syntax, etc.)
- Declare the target shell in the shebang: `#!/usr/bin/env bash`

## Operating system
- Target **Ubuntu LTS** (current and previous release) by default
- Declare supported OS and versions in `README.md`
- If the script relies on OS-specific tools, document the assumption and add a compatibility check at startup
