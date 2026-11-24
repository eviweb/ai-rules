# Evolvability

Read when the project is meant to live beyond a one-off: anything with users, versions or a future maintainer. It covers the ISO/IEC 25010 sub-characteristics of maintainability (modularity, reusability, analysability, modifiability, testability) and flexibility (adaptability, scalability, installability, replaceability).

## Keep the cost of change visible

- **Hotspots**: the files that change most are where structure matters most (`git log --name-only | sort | uniq -c | sort -rn`). Combine with complexity before deciding where to refactor (`ai-rules-refactoring-and-design`).
- **Change coupling**: files that always change together belong together or hide a missing abstraction.
- Watch the DORA indicators: deployment frequency, lead time for changes, change failure rate and time to restore service. Use them to see trends, not to rank people.

## Technical debt

Debt is a conscious loan: it speeds up now and costs interest later. Fowler's quadrant helps to talk about it: **deliberate or inadvertent**, **prudent or reckless**. Only deliberate and prudent debt is a decision; the rest is a defect in the process.

- Keep a register: in `TODO.md` as `[debt]` lines for a light project, as issues for a strict one (see `ai-rules-refactoring-and-design`).
- Each entry says what, why it was accepted, the cost it adds, and the condition for repaying it.
- Pay down debt in small steps, beside the feature work, not in a big-bang rewrite.

## Decisions: ADR

Record each significant decision in a short **architecture decision record** in `docs/design/adr/NNNN-title.md`: context, options considered, decision, consequences. A later reader (or agent) can then tell a deliberate choice from an accident, and knows when to revisit it. Supersede an ADR, do not edit its history.

## Fitness functions: protect properties automatically

Turn each architectural intention into an automated check run in CI, so it cannot erode silently:

- layer and dependency rules (`import-linter`, `dependency-cruiser`, `deptrac`), no cycles;
- size budgets and complexity ceilings; a coverage floor on the code that matters;
- performance and startup budgets; public-API compatibility checks.

ai-rules itself does this for its context budgets and skill formats.

## Contracts and deprecation

- Version every public contract (`rules/versioning.md`, `rules/compatibility.md`); additive changes are non-breaking.
- Deprecation path: announce, warn at use, keep for a stated number of versions, remove. Migrations use **expand and contract**; databases and wire formats too.
- Keep an upgrade path for dependencies: update regularly, in small steps, rather than in rare large jumps.

## Reversibility and timing

Prefer decisions that are cheap to undo; defer the others to the last responsible moment, when the information exists. Isolate third-party dependencies behind a boundary you own, so replacing them is local.

## Red flags

Nobody knows why a module is shaped as it is; a rewrite proposed because small steps look impossible; dependency updates that need a project of their own; tests that must be edited for every change; an architecture that exists only in someone's head.
