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
