# Maintainability
The codebase can be understood, modified, and extended by anyone familiar with the language — including yourself six months from now.

- Names are explicit and describe intent — no abbreviations, no single-letter variables outside loops
- Functions do one thing; if a function needs a comment to explain what it does, rename it or split it
- No dead code, no commented-out blocks, no untracked TODOs
- Complexity is documented where unavoidable (non-obvious invariant, external constraint, workaround for a known bug)
- See `core/principles.md` and `rules/naming.md`

Red flags: functions > 50 lines, deeply nested conditions, magic numbers, copy-paste logic, code that only the original author can explain.
