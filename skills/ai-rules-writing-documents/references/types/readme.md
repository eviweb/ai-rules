# README

The README answers, in this order: what is it, should I use it, how do I get it running. A visitor decides in under a minute; everything else is linked.

## Sections, in order

1. **Name and one-sentence description**: what it does and for whom, without jargon.
2. **Status and badges** (optional, few): CI, version, licence. No decorative badges.
3. **Why or features** (short): the problem solved and the three to five main capabilities.
4. **Requirements**: supported systems and versions (`rules/compatibility.md`), external tools.
5. **Installation**: copy-pasteable commands, tested.
6. **Quick start**: the smallest useful example with its output.
7. **Usage**: the main commands or API, or a link to the guides when they are long.
8. **Configuration**: keys, environment variables (in sync with `.env.example`), defaults.
9. **Project profile** (`core/git.md`) and any **artifact language** other than English (`core/language.md`).
10. **Contributing, licence, links**: pointers to `CONTRIBUTING.md`, `LICENSE.md`, `CHANGELOG.md`, the docs.

## Rules

- The quick start works on a clean machine, copied as is. Check it after every change to installation or commands.
- Move content to `docs/` when a section exceeds a screen; keep a one-line summary and a link.
- No changelog, roadmap or design history in the README: link to them.
- State the version or date only where it matters, and read it from `VERSION`, not from memory.
