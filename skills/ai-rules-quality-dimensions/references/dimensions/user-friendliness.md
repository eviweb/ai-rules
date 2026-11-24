# User-friendliness
The system is easy to use correctly and hard to use incorrectly.

- Error messages tell the user what went wrong, why, and how to fix it
- Defaults are sensible — the common case requires no configuration
- `--help` is complete, accurate, and includes examples
- Destructive operations require explicit confirmation or a `--dry-run` preview
- Output is readable: use colour when appropriate, respect `NO_COLOR`, format tables clearly
- Usability heuristics, inclusive design and CLI/API ergonomics: [user-centric design](../contexts/user-centric.md)

Red flags: cryptic error codes without explanation, no `--help`, silent success for operations that changed nothing, irreversible actions without confirmation.
