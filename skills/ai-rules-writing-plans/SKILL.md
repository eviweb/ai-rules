---
name: ai-rules-writing-plans
description: "Use when an approved spec or design needs several steps to implement, before touching code: inspect the repository, split the work into right-sized tasks with exact files, interfaces, tests, a model tier and commit points, then have the user review the plan."
metadata:
  derived-from: "superpowers/writing-plans @ 22f0b46"
  license-of-origin: MIT
---
# Writing plans

A plan holds the decisions an implementer cannot make alone: which files, which names and signatures, which values from the spec, which tests prove each task. Write it for a capable developer who has seen neither the code base nor the conversation. It is not the code: a plan longer than the code it describes has written the code instead.

## Before the first task

1. **Inspect the repository**: layout, conventions, test command, CI, `TODO.md`, the files the change touches and their tests. Follow the existing patterns; a split of a file that has grown unwieldy may be a task, a wider restructuring is proposed separately (`core/principles.md`).
2. **Check the scope**: if the spec covers independent subsystems, propose one plan each, each producing working, tested software on its own.
3. **Map the files**: which files are created or modified and what each is responsible for. Files that change together live together; split by responsibility, not by technical layer.

## Tasks

A task is the smallest unit with its own test cycle that a reviewer could accept or reject on its own. Fold setup, configuration and docs into the task whose deliverable needs them.

Each task carries:

- **Files**: create, modify (with line ranges when useful), test.
- **Interfaces**: what it consumes from earlier tasks and what it produces for later ones, with exact names and types.
- **Ready**: goal, acceptance criteria, constraints, how to verify (definition of ready). A task that cannot be made ready names what is missing.
- **Steps**, each one action with a checkable result: write the failing test (name and assertions, with the spec's exact values), run it and the expected failure, implement (exact signature and file; a body only for an algorithm the tests do not determine), run it and the expected pass, refactor (`rules/tdd.md`).
- **Done**: tests pass, docs and changelog updated, verification shown (definition of done, `ai-rules-verification-before-completion`).
- **Tier**: `light` (mechanical, fully specified), `standard` (usual implementation), `deep` (design judgement, tricky debugging, security). See *Model tiers*.

**Commit points.** Mark where a commit is proposed. Default: one commit per branch, so one pull request per topic (`core/git.md`). Add a commit point inside a branch only when it makes review easier. The agent never commits: at each point it writes `.private/COMMIT_MESSAGE` and waits (`core/commits.md`).

## Plan document

Save it as `.private/plans/YYYY-MM-DD-<topic>.md` unless the project keeps plans elsewhere. It starts with:

```markdown
# <Topic> plan

**Goal:** one sentence. **Spec:** path to the spec or design. **Branch:** name.
**Approach:** two or three sentences. **Stack:** key tools and libraries.

## Global constraints
One line each, values copied from the spec (versions, limits, naming, platforms).

## Review focus
Up to five inputs or failure modes the spec implies but no task's tests exercise, most likely first; each gets a test in the task that owns the code.

## Progress
Tasks ticked when done; rulings (decisions taken during execution) and deferred findings, one line each.
```

## Model tiers

Give each task a tier, never a model name. If `~/.config/ai-rules/model-tiers.md` exists, add the matching model and effort next to the tier, and if its `checked:` date is older than three months, add one line asking the user to run `/model` and update it. If it does not exist, say once that it can be created and show the template:

```markdown
light: <model>, effort <low|medium|high>
standard: <model>, effort <…>
deep: <model>, effort <…>
checked: YYYY-MM-DD
```

with where to find the values: the agent's `/model` command (the models and efforts the user's plan allows) and the vendor's public models page. Do not look them up yourself. `ai-rules status` reports a missing or stale file without any token cost. When the running model or effort does not match the tier of the next task, say it in one line; never switch models on your own.

## Self-review

Before showing the plan, check it against the spec:

1. **Coverage**: each requirement has a task.
2. **Steps**: each step lets the implementer write exactly one reasonable thing; remove lines that decide nothing ("handle edge cases", "TBD") and bodies the tests already determine.
3. **Consistency**: names and types match across tasks.
4. **Review focus**: filled, or stated empty after checking.
5. **Proportion**: if code blocks are most of the plan, replace bodies with signatures and test names.

Fix what you find, then give the user the plan path and a summary (tasks, tiers, commit points), and ask them to review it. Execution starts only after their go, with `ai-rules-executing-plans`.
