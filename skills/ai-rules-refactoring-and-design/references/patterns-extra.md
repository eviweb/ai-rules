# Rarer patterns (read on request)

Use when the problem in the index of `patterns.md` matches, or when the user asks. Same rule: only if the problem is real.

- **Bridge**. Use: two dimensions vary independently (for example shape and renderer) and subclassing would multiply classes. Avoid: one dimension varies.
- **Flyweight**. Use: very many small objects sharing most of their state, with a measured memory problem. Avoid: without a measurement.
- **Interpreter**. Use: a small, stable grammar (rules, queries, filters) worth an object model. Avoid: anything non-trivial; use a parser library.
- **Iterator**. Use: expose a custom traversal without leaking structure. Avoid: nearly always already built in (generators, iterators, ranges); do not hand-write one.
- **Memento**. Use: undo or snapshot an object's state without exposing internals. Avoid: when copying plain immutable data is enough.
- **Mediator**. Use: many objects interact in tangled ways (a form, a dialog); route them through one coordinator. Avoid: the coordinator becomes a god object.
- **Prototype**. Use: create objects by cloning a configured instance when construction is costly. Avoid: languages where copy or dataclass replace is trivial.
- **Visitor**. Use: add operations over a stable class hierarchy (syntax trees, document models) without editing the classes. Avoid: when the hierarchy changes often, or the language has pattern matching.
