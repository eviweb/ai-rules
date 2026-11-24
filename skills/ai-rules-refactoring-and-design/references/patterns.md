# Design patterns

A pattern names a solution to a recurring problem. Apply it only when its problem is present and a simpler structure does not solve it. Patterns usually emerge from refactoring (Kerievsky): refactor toward one, do not start from one.

## Index: problem to pattern (all 23 GoF patterns)

| Problem | Pattern | Detail |
|---------|---------|--------|
| Interchangeable algorithms chosen at runtime | Strategy | here |
| Object creation hidden behind a method | Factory Method | here |
| Families of related objects created together | Abstract Factory | here |
| Many optional parameters when constructing | Builder | here |
| Make an incompatible interface fit | Adapter | here |
| Add behavior around an object without subclassing | Decorator | here |
| Simplify a subsystem behind one entry point | Facade | here |
| Treat a tree of parts like a single part | Composite | here |
| Notify dependents when something changes | Observer | here |
| Turn a request into an object (queue, undo, log) | Command | here |
| Fixed algorithm skeleton, variable steps | Template Method | here |
| Behavior depends on state and changes with it | State | here |
| Pass a request along a chain until handled (middleware) | Chain of Responsibility | here |
| Control access, cache or load lazily | Proxy | here |
| Remove null checks with a neutral object | Null Object (not GoF) | here |
| Pass collaborators in instead of building them | Dependency Injection (not GoF) | here |
| Vary abstraction and implementation separately | Bridge | extra |
| Share many small objects to save memory | Flyweight | extra |
| Evaluate a small language or grammar | Interpreter | extra |
| Traverse a collection without exposing it | Iterator | extra (built into most languages) |
| Save and restore an object's state | Memento | extra |
| Centralize how objects talk to each other | Mediator | extra |
| Create objects by copying a prototype | Prototype | extra |
| New operations over a stable structure without editing it | Visitor | extra |
| One instance only | Singleton | avoid: global state in disguise |

The eight "extra" patterns are detailed in `patterns-extra.md`, read on request.

## The patterns in detail

For each: use it when, avoid it when.

- **Strategy**. Use: several algorithms for one job, chosen by configuration or context; replaces a repeated switch. Avoid: two cases that will not grow (a function argument is enough).
- **Factory Method / Abstract Factory**. Use: callers must not know the concrete class, or a family must stay consistent. Avoid: one concrete class and no variation.
- **Builder**. Use: construction with many optional parts or validation across them. Avoid: a constructor or keyword arguments suffice.
- **Adapter**. Use: wrap a third-party or legacy interface at the boundary so the rest depends on yours. Avoid: adapting your own code (change it).
- **Decorator**. Use: stack optional behavior (logging, caching, retry) on the same interface. Avoid: when a plain wrapper function reads better.
- **Facade**. Use: a simple front for a complex subsystem or library. Avoid: when it only forwards calls (Middle Man).
- **Composite**. Use: trees where leaf and group are used alike (files, UI, expressions). Avoid: flat data.
- **Observer**. Use: one-to-many notification with loose coupling (events, hooks). Avoid: when ordering and flow must be explicit; watch for leaks and cycles.
- **Command**. Use: queue, retry, undo, audit trail, macros. Avoid: a direct call is enough.
- **Template Method**. Use: a fixed sequence with a few overridable steps. Avoid: deep subclassing; prefer Strategy when the variation is independent.
- **State**. Use: many conditionals on a status field with transitions. Avoid: two or three states without behavior differences (an enum and a switch).
- **Chain of Responsibility**. Use: ordered handlers that may stop or pass a request (HTTP middleware, validation pipelines). Avoid: one handler.
- **Proxy**. Use: lazy loading, caching, access control, remote calls behind the same interface. Avoid: when the indirection hides cost or failure modes callers must know.
- **Null Object**. Use: a default do-nothing behavior instead of repeated null checks. Avoid: when absence is an error to surface.
- **Dependency Injection**. Use: pass collaborators in (constructor or parameter) for tests and swapping. Avoid: a container framework for a small program; plain parameters do.

## Architectural patterns (names to recognize; the choice is `ai-rules-architecture-proposal`)

Layered, hexagonal (ports and adapters), clean architecture (dependencies point inward), pipes and filters, plugin or registry (`agents.toml` is one), MVC, MVP, MVVM, repository, service layer, unit of work, modular monolith, event-driven, CQRS, event sourcing. CQRS and event sourcing are not recommended here: heavy for the usual size of these projects.

Resilience patterns: timeout, retry with backoff, circuit breaker, bulkhead, idempotency key (`ai-rules-quality-dimensions`).

## Anti-patterns to name when seen

God object, Big Ball of Mud, Golden Hammer (one tool for every job), Lava Flow (dead code nobody dares remove), Cargo Cult (copied without understanding), premature abstraction, over-engineering, Not Invented Here, Singleton and Service Locator as hidden dependencies, anemic domain model when the domain has real rules.
