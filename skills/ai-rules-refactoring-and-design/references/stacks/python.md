# Python

## Idioms
- `dataclass` (frozen when possible), `enum`, `Protocol` for structural interfaces, `pathlib`, context managers, generators and comprehensions.
- Type hints at module boundaries; pure functions for logic, I/O at the edges; `logging`, never `print`, in libraries.

## Signals
- Mutable default argument, bare `except` or `except Exception`, a module that does everything, circular imports.
- `isinstance` chains (replace with polymorphism or `match`), stringly typed parameters, module-level mutable state.

## Detectors
- `ruff` rules: `C901` (complexity), `PLR` (too many arguments, branches, statements), `SIM` (simplify), `B` (bugbear), `RET`, `PERF`, `ARG`, `ERA` (commented-out code).
- `vulture` (dead code), `radon cc` and `radon mi` (complexity and maintainability), `mypy` or `pyright` (types), `import-linter` (layer contracts, cycles), `bandit` (security).
- `pytest --cov`, `mutmut` (are the tests strong enough to refactor under?).
- Automated rewrites: `ruff --fix`, `pyupgrade`, `libcst` codemods.
