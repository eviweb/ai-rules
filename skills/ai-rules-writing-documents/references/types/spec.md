# Specification

A specification says **what** to build and **how to tell it is done**, not how to build it (that is the [design document](design-doc.md)). Write it before the plan; it is the input of `ai-rules-writing-plans` and the source of the acceptance tests.

## Pick the tier by size and risk

| Tier | When | Form |
|---|---|---|
| Light | A small, low-risk change | A few lines in the issue or the PR: goal, acceptance criteria |
| Standard | A feature over several tasks | `docs/specs/NNNN-title.md` with the sections below |
| Full | Several components, external users, regulated or safety-relevant behavior | Standard plus quality scenarios, data and interface contracts, traceability from requirement to test |

## Sections (standard tier)

1. **Problem and goal**: who has the problem, what they cannot do today, the outcome that measures success.
2. **Users and scenarios**: the main use cases, in the user's words.
3. **Requirements**: numbered (`R1`, `R2`…), each one testable. Write them in **EARS** form:
   - ubiquitous: "The CLI shall write errors to stderr."
   - event: "When the config file is missing, the CLI shall exit with code 2."
   - state: "While a sync runs, the CLI shall refuse a second sync."
   - unwanted behavior: "If the target is not writable, then the CLI shall report the path and abort."
   - optional feature: "Where `--dry-run` is given, the CLI shall print the changes without applying them."
4. **Acceptance criteria**: one or more per requirement, in **Given-When-Then** form, each one a future test.

   ```gherkin
   Given a repository without agents.toml
   When the user runs "ai-rules install"
   Then the command exits with code 2
   And stderr names the missing file
   ```

5. **Quality requirements**: the critical dimensions from `ai-rules-quality-dimensions`, as measurable scenarios.
6. **Non-goals**: what this work deliberately does not do. They prevent scope creep and answer the reviewer's "what about…?".
7. **Open questions**: each with an owner or a decision date. A spec with open questions on a requirement is not ready to plan.

## Rules

- One requirement per sentence; "shall" for mandatory, no "should" or "may" hidden in a requirement.
- No solution in the requirements unless it is a real constraint (an imposed format, an existing API).
- Ban unmeasurable words: "fast", "user-friendly", "robust", "flexible". Give the number or the observable behavior.
- Keep the spec in sync with what is built: a requirement changed during implementation is changed in the spec in the same PR.
