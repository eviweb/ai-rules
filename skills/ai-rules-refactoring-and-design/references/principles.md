# Design principles

One line each: the rule, then the signal that it is being broken. Arbiter order and conflicts are in `SKILL.md`. Names and ideas come from the literature listed at the end; the wording is ours.

## Simplicity

- **KISS**: the simplest design that meets the need. Signal: a reader needs a diagram to follow a ten-line behavior.
- **YAGNI**: build what is required now (`core/principles.md`). Signal: parameters, hooks or layers nobody calls.
- **Four rules of simple design** (Beck), in order: the tests pass; the code reveals its intent; no duplicated knowledge; the fewest elements. This is the arbiter order of `SKILL.md`.
- **Convention over configuration**: sensible defaults and conventions remove decisions; configure only what differs. Signal: setup the user must repeat for every project.
- **Least astonishment**: names, signatures and behavior agree. Signal: a function that does more than its name says.
- **Explicit over implicit**: dependencies, units, errors and defaults are visible at the call site. Signal: hidden globals, magic values, implicit conversions.
- **Make it work, make it right, make it fast**, in that order. Measure before optimizing (Knuth). Signal: optimization without a measurement.

## Structure

- **Separation of concerns**: one concern per unit. Signal: parsing, business rules and I/O in the same function.
- **High cohesion, low coupling**: things that change together live together; modules know little of each other. Signal: shotgun surgery, long import lists.
- **Encapsulation, information hiding** (Parnas): a module hides the decision most likely to change. Signal: callers depend on internals.
- **SOLID**, each letter on its own signal:
  - *SRP*: one reason to change. Signal: divergent change.
  - *OCP*: extend by adding code, not editing the stable one. Signal: the same switch edited for every new case.
  - *LSP*: a subtype works wherever its parent does. Signal: a subclass that throws or ignores inherited behavior.
  - *ISP*: small client-specific interfaces. Signal: implementations with empty or failing methods.
  - *DIP*: depend on abstractions at boundaries, inject the concrete. Signal: business code constructing its own database or HTTP client.
- **Composition over inheritance**: assemble behavior, inherit only for a true "is a". Signal: refused bequest, deep hierarchies.
- **Tell, don't ask; Law of Demeter**: ask an object to act instead of pulling its data, and talk to neighbors only. Signal: `a.b().c().d()` chains, feature envy.
- **Command-query separation** (Meyer): a function either changes state or returns information. Signal: a getter with side effects.
- **DRY with the rule of three**: one source for each piece of knowledge, extracted at the third occurrence. A wrong abstraction costs more than duplication. Signal: two look-alike blocks that change for different reasons must stay apart.
- **Orthogonality**: changing one thing does not force changes in unrelated things.
- **Single source of truth**: one place defines a value (`VERSION`), others derive from it.

## Behavior and data

- **Fail fast**, explicit errors (`rules/error-handling.md`). Signal: swallowed exceptions, `|| true`.
- **Pure functions, immutability by default, functional core and imperative shell**: decisions in pure code, side effects at the edges. Signal: tests needing heavy setup.
- **Parse, don't validate; make illegal states unrepresentable**: convert input once at the boundary into a type that cannot be invalid. Signal: the same check repeated deep in the code.
- **Design by contract**: state preconditions, postconditions and invariants; they tell what to test and assert.
- **Idempotence** for operations that may be retried (scripts, PUT, deployments). Signal: a rerun that breaks or duplicates.
- **Postel's law is not adopted**: lenient input hides faults; validate strictly at the boundary.

## Change

- **Two hats, preparatory refactoring, Chesterton's fence, restricted boy-scout rule**: see `SKILL.md`.
- **Reversibility**: prefer decisions that are cheap to undo; defer the others until the information arrives. Signal: a one-way door taken on a guess.
- **Tracer bullet, walking skeleton**: a thin end-to-end slice first, then thicken. Signal: a layer built completely before anything runs.
- **Tidy first**: small safe cleanups right before a change, in their own commit.

## Working method

- **Design thinking** (core only): frame the problem before the solution: who has it, what success looks like; prototype cheaply; test with real users or real use. No workshops.
- **Modern Agile**: make people awesome; make safety a prerequisite; experiment and learn rapidly; deliver value continuously. Practical meaning here: small reversible steps, explicit rollback, feedback after each release.
- **Spike**: a time-boxed exploration to remove one technical uncertainty before committing to a design; its output is an answer and a note, not production code. Say the time box and the question first.
- **Definition of ready**: a task is ready when its goal, acceptance criteria, constraints and the way to verify it are written. Ask for what is missing before starting.
- **Definition of done**: a task is done when its acceptance criteria are met and shown (`ai-rules-verification-before-completion`), tests pass, docs and changelog are updated, and the review checklist is done (`core/commits.md`).

## Systems and teams

- **Unix philosophy**: small tools doing one thing, composed through plain text; suits shell and CLIs.
- **Twelve-factor** for services: config in the environment, logs as streams, stateless processes, disposability.
- **Conway's law**: the system mirrors the communication structure of its authors; consider it when drawing module boundaries.
- **Hyrum's law**: with enough users, every observable behavior is depended upon; version and deprecate with care (`rules/compatibility.md`).
- **Package principles** (stable dependencies, acyclic dependencies, common closure and reuse): only for large modular codebases.

## Values handled elsewhere

Security and privacy by design, accessibility, user-centric design, evolvability, reliability and the other ISO/IEC 25010 characteristics: `ai-rules-quality-dimensions`.

## Sources

Fowler, *Refactoring* (2nd ed.); Kerievsky, *Refactoring to Patterns*; Feathers, *Working Effectively with Legacy Code*; Martin, *Clean Code* and *Clean Architecture*; Gamma et al., *Design Patterns*; Hunt and Thomas, *The Pragmatic Programmer*; Beck, *Tidy First?*; Meyer, *Object-Oriented Software Construction*; Parnas (1972); Evans, *Domain-Driven Design*. Ideas only, no text reproduced.
