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
