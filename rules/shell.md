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
