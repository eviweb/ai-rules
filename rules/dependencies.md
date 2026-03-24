# Dependencies

- Pin dependency versions explicitly — never use unpinned or wildcard versions in production
- Prefer actively maintained packages with a clear release history
- Run a security audit before each release (e.g. `npm audit`, `pip audit`, or equivalent)
- Keep dependencies up to date; review and update regularly
- Minimize the number of dependencies — prefer standard library or well-established tools over niche packages
- Document why each non-obvious dependency was chosen (in `README.md` or inline comment)
