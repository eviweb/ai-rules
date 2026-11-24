# Language-independent tools and checks

Propose a tool the project does not use yet; never add it silently.

## No tool needed
- **History**: `git log -S'<text>'` and `git blame` find why code exists (Chesterton's fence).
- **Hotspots** (files that change most; combine with complexity to find where refactoring pays):
  `git log --since=1.year --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20`
- **Dead code check**: search all references (`grep -rn`, the language server) before removing.

## Tools
- `jscpd`: copy-paste detection across many languages.
- `lizard`: cyclomatic complexity and function length for most languages.
- `semgrep`: custom pattern rules and security checks.
- `cloc`: size by language, to choose where to look first.
- Mutation testing (per stack): measures whether the tests would catch a change; worth running before a large refactoring.
- Coverage: a safety net, not a goal; check the code you are about to change is covered.
