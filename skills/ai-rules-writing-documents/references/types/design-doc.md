# Design document

A design document says **how** a specified change will be built and why this way. Write one when the change spans several components, is hard to undo, or reviewers would otherwise discover the design in the diff. For a single structural decision, an ADR is enough (`ai-rules-architecture-proposal`). Keep it in `docs/design/NNNN-title.md`.

## Sections

1. **Context and scope**: the problem in two or three sentences, a link to the spec, what is in and out of scope.
2. **Goals and non-goals**: from the spec, plus the technical ones (for example "no new runtime dependency").
3. **Proposed design**: the overview first (one diagram, see [diagrams](../diagrams.md)), then the parts that need explanation: components and their responsibilities, interfaces and data formats, data flow, error handling, migration of existing data or users.
4. **Alternatives considered**: each with why it was not chosen. A design without alternatives was not designed, it was assumed.
5. **Cross-cutting concerns**: only those that apply: security and privacy (threats, data handled), accessibility, performance, observability, compatibility and deprecation, operations (deployment, rollback).
6. **Risks and open questions**: the riskiest assumption and how it will be checked (spike, prototype, measure).
7. **Rollout and testing**: the order of the slices, feature flags if any, the test strategy for each part.

## Rules

- Length follows risk: two pages are usually enough; a design document that nobody reads before the review failed.
- Show the design to the user before implementation and record the decision; update the document if the implementation diverges, or mark it as superseded.
- Explain trade-offs, not only choices: what this design costs and what would make it wrong.
