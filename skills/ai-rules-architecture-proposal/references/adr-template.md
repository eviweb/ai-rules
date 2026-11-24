# ADR template

File: `docs/design/adr/NNNN-short-title.md`, numbered in order. One decision per file. Never rewrite an accepted ADR: supersede it with a new one and link both.

```markdown
# NNNN. Title of the decision

- Status: proposed | accepted | superseded by NNNN | deprecated
- Date: YYYY-MM-DD
- Deciders: who validated it

## Context
The problem, the constraints and the forces at play, in a few lines.

## Options considered
1. Option A: one line, what it optimizes.
2. Option B: one line.
3. Option C: one line.

## Quality scenarios
For the two or three critical criteria, one measurable scenario each (for example "with 100 concurrent users, the main page answers in under 1 s"). They become tests or fitness functions.

## Riskiest assumption
The assumption the decision depends on most, and how it is checked (a spike, a measurement, a conversation).

## Decision
The option chosen, in one or two sentences, and why it wins on the criteria that matter.

## Consequences
- Positive: what becomes easier.
- Negative: what becomes harder, and the debt accepted.
- Risks and how they are limited.

## Exit plan
How to leave this choice if it proves wrong: what would be replaced, in how many steps, at what cost.

## Revisit when
The observable triggers that would justify reopening the decision, and a checkpoint after the first slice is delivered, to compare the predictions with what happened.
```

Keep it to one page. A decision that is hard to explain in one page is probably two decisions.
