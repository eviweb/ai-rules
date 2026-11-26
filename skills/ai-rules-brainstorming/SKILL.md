---
name: ai-rules-brainstorming
description: "Use when about to build something new or change behavior and what the user wants, or why, is not fully settled: understand the need, lay out the approaches, size the work, and get the design approved before any implementation."
metadata:
  derived-from: "superpowers/brainstorming @ 22f0b46"
  license-of-origin: MIT
---
# Brainstorming

What gets built rests on what you believe the user wants, and that belief is usually thinner than it feels. Find out what they want and why before anything is built; the why lets you make the many small decisions they will never mention the way they would. This is the design-thinking core: frame the problem before the solution, try cheaply, learn from real use.

## First: what do you know?

- **Everything that matters is in the request** ("rename the option to `--dry-run`"): no brainstorming. Do it through the normal flow and say what you did.
- **Something that would change the result is missing**: start the conversation below.
- **The user asks what to do next** (a version, a batch of work): go to *Rank the candidates*.

## Look before you ask

In an existing project, or when the user gave context (a spec, an issue, a handoff note, files), read it and the code it touches first, until you can explain how the relevant parts work today and what the change would touch. Never ask what the project already answers or reopen what the user already decided.

## The conversation

- **Ask only what changes what gets built**, one question at a time, in the user's words, never process jargon. Say why you ask: what the answer would change.
- **Get them describing first.** Until you know why they want it, ask open questions with no options attached: options steer. Once the why is known, sketch the choices concretely with what each trades off and which you would pick.
- **Ground to cover**, as territory, not as a questionnaire: what it is and for whom, why now and what success looks like, goals, non-goals and anti-goals (what would make it a failure even if it works), prior art, current state, the details they care about.
- **State your calls.** Process choices (where files go, what to read next) are yours: do them and say so. A default you fill in is said out loud as a proposal they can reject, never presented as agreed.
- **Play back as you go**: once a part is understood, describe it back in a short paragraph, mark what you filled in as your proposal, and ask what is wrong or missing.
- **Show, don't tell**: a few lines of text sketch for a screen or an output, a Mermaid diagram for a flow or a structure (`ai-rules-writing-documents`).
- **Spike** when a quick throwaway build is the cheapest way to learn: say the question and the time box, get a yes, then bring back the answer. A spike has no plan and minimal tests; keeping its code is a new request that goes through this skill again.

## Lay out the approaches

Once you understand what they want, and before writing anything up, give the ways of building it in a message of its own: find several, drop the weak ones (against the why, ruled out by the existing code), keep two or three, sketch each concretely with its trade-offs, recommend one and say why, and ask. If there is truly one sensible way, say so and why the others do not fit. For a new project or a significant component, this step is `ai-rules-architecture-proposal`.

## Size the work and write the design

Once an approach is chosen, say how big the work is; the user can override.

| Size | Written output |
|---|---|
| Small change | A few lines in the issue or the conversation: goal, approach chosen, acceptance criteria |
| Feature | A specification in `docs/specs/` (`ai-rules-writing-documents`, `types/spec.md`), with the approaches considered |
| Project or several components | Specification plus design document in `docs/design/` |

If the work grows mid-way, stop, say so and step up a size. If it is really several independent projects, say so, agree on an order and handle them one at a time.

Before handing the document over, read it as a builder who was not in the conversation: questions the conversation already answered go into the document; minor ones you settle and mark as your call; the ones only the user can answer go to them in one message, most important first.

## Rank the candidates

When the user asks what to do next, inspect the repository first (`TODO.md`, open issues, recent history, failing checks), then propose the candidates in one table: value for the user, complexity or risk (low, medium, high, with a reason when not obvious), dependencies. Order by value over complexity, recommend a batch, update `TODO.md` once the user validates.

## Gate

Nothing is built until the user approves the design: no production code, scaffolding, dependency installation or implementation skill. Reading and exploring are fine. Two exceptions: the user opted out of the questions ("just do it"; state any significant how-it-gets-made choice in one line, then go), or an approved spike. After approval, the next step is `ai-rules-writing-plans`.

## Red flags

| Thought | Reality |
|---|---|
| "I'll offer a menu of what they might want" | Options steer. Ask them to describe it first |
| "I'll fill in sensible defaults" | Say them out loud; a default they never heard is one they could not reject |
| "They said 'sounds good' to the idea" | Approval covers what they saw. An unwritten design is not approved |
| "The spike works, I'll keep building on it" | Keeping it is a new request |
