# Security

- Never hardcode credentials, tokens, API keys, or passwords in source files
- Use environment variables or a secret manager for sensitive values
- Add secret files (`.env`, `*.key`, `*_token`, etc.) to `.gitignore` before the first commit
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
