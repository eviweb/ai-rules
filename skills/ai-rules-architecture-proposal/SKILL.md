---
name: ai-rules-architecture-proposal
description: "Use when starting a project or adding a significant component, before choosing a structure: compare at least three architectures against the project's criteria, recommend one, wait for validation, then record an ADR."
---
# Architecture proposal

Do not pick an architecture silently and do not scaffold before the user has chosen. Present the options with their trade-offs (`core/principles.md`: propose options before deciding), recommend one, and wait.

Use it at project start, for a new significant component, or when a structural change is being considered (for example after a refactoring proposal from `ai-rules-refactoring-and-design`). Skip it for a change that fits the existing structure.

## Procedure

1. **Frame.** In a few lines: the goal and the users, the constraints (deadline, skills, target environments from `rules/compatibility.md`, existing code), the expected size (users, data volume, number of integrations, team, lifetime) and the non-goals. Ask up to five questions if something decisive is missing; do not guess it.
2. **Find the criteria.** Start from the critical dimensions of `ai-rules-quality-dimensions` and the contexts that apply (interface, personal data, network exposure, end users, longevity). Add the common criteria of [criteria](references/criteria.md). Keep six to ten criteria, not more. For the two or three most critical, write a **quality scenario**: a measurable sentence ("with 100 concurrent users the main page answers in under 1 s") that will later become a test or a fitness function.
3. **Propose at least three candidates**, taken from [architectures](references/architectures.md) or adapted. Always include **the simplest thing that could work**, one that goes further than today's need so that the cost of growth is visible, and **an existing tool, library or service** that already does the job (reuse before build; count its lock-in and licence). A candidate has a name, a two-line description and what it optimizes.
4. **Compare** in one table: candidates in columns, criteria in rows, a short rating per cell (`++`, `+`, `0`, `-`, `--`) with a reason when it is not obvious. Add the rows that always matter: **effort to build**, **running cost and operational burden**, **reversibility** (how hard it is to move away). No weighted scores: false precision hides the judgement. See the [example](references/example.md).
5. **Test the riskiest assumption.** Name the assumption the recommendation depends on most (performance, an integration, a cost). If it can be checked cheaply, propose a time-boxed **spike** (a question, a time limit, throwaway code) before the decision.
6. **Sketch the threats** when the contexts of `ai-rules-quality-dimensions` for security or privacy apply: a one-page data-flow diagram of the recommended option and a STRIDE pass, with the mitigations or the accepted risks.
7. **Recommend** one, with the reasons, the main risks and how to limit them, an **exit plan** (how to leave this choice, in how many steps) and **what would change the recommendation** (a trigger such as "a second client appears" or "the team grows beyond three"). Propose the **first slice**: a thin end-to-end piece to build first.
8. **Wait for the user's decision.** Answer questions, rework the table if a criterion was missing, never start building meanwhile.
9. **Record the decision** as an ADR in `docs/design/adr/NNNN-title.md` from the [template](references/adr-template.md): quality scenarios, riskiest assumption, rejected options, exit plan, revisit triggers. After the first slice is delivered, check the predictions against what happened and update the status. Later changes supersede the ADR with a new one; they do not rewrite it.

## Rules of thumb

- **KISS and YAGNI decide ties** (`core/principles.md`): the architecture must fit today's need and be cheap to evolve, not fit imagined scale.
- A style is a means. Choose by the criteria, not by fashion or by what the agent knows best.
- Microservices, event sourcing and similar are operational and organizational choices; recommend them only with evidence of the need (independent teams, independent scaling, hard isolation) and say what they cost.
- Prefer decisions that are cheap to undo and delay the others until the information exists. Isolate what is likely to change (a third-party service, the storage, the interface) behind a boundary you own.
- Treat a quality requirement you cannot meet in the recommended option as a stated trade-off, not a silent gap.
- Also decide, at the same time and in the same way, the few technology choices that follow from it (language, test framework as in `rules/tdd.md`, storage, packaging, deployment): one short table each, with the simplest option first.
- A small component diagram helps (boxes and arrows, with a text description next to it); a full specification is a separate step.

## In ai-rules

The skill produces a proposal and, once validated, an ADR draft. It writes no code, scaffolds nothing and never commits; the commit gate of `core/commits.md` applies to the ADR.
