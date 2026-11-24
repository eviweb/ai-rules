# Code smells

A smell is a hint that structure may be hurting change, not a defect. Check cost and risk before acting. Techniques are described in `refactorings.md`.

## Thresholds

Indicative only. When the project has a linter configuration (`ruff`, `eslint`, `golangci-lint`, `phpstan`…), its thresholds win. Without one: a function over about 50 lines (as in `quality.md`), more than 5 parameters (the `ruff` default), nesting over 3, cyclomatic complexity over 10 (McCabe), cognitive complexity over 15 (Sonar). Crossing a threshold triggers a look, not an automatic change: judge whether the code really hinders the change, and say "flagged, left as is" for stable code that nobody reads.

## Bloaters

| Smell | Signal | Technique |
|-------|--------|-----------|
| Long Function | over about 50 lines, or a block needing a comment | Extract Function, Replace Temp with Query, Decompose Conditional |
| Large Class / module | many unrelated fields and methods | Extract Class, Extract Superclass |
| Long Parameter List | more than about 4 | Introduce Parameter Object, Preserve Whole Object, Replace Parameter with Query |
| Data Clumps | the same few values travel together | Introduce Parameter Object, Extract Class |
| Primitive Obsession | strings and numbers standing for domain concepts | Replace Primitive with Object, Replace Type Code |

## Change preventers

| Smell | Signal | Technique |
|-------|--------|-----------|
| Divergent Change | one module edited for unrelated reasons | Extract Class, Split Phase |
| Shotgun Surgery | one change touches many modules | Move Function, Inline Class (structural: report) |
| Parallel Inheritance Hierarchies | adding a class forces adding another | Move Function, collapse one hierarchy |

## Dispensables

| Smell | Signal | Technique |
|-------|--------|-----------|
| Duplicated Code | same knowledge in several places | Extract Function, Pull Up, Slide Statements |
| Dead Code | unreachable or unused | Remove Dead Code (check history first) |
| Speculative Generality | hooks and parameters for a future that did not come | Inline, Collapse Hierarchy, Remove Parameter |
| Lazy Element | a class or function that does too little | Inline Function, Inline Class |
| Temporary Field | field set only in some paths | Extract Class, Introduce Special Case |
| Comments as deodorant | a comment explains confusing code | Extract Function, Rename, then drop the comment |
| Mysterious Name | a name that needs a decoder | Rename, Change Function Declaration |
| Magic numbers and strings | unexplained literals | named constants |

## Couplers

| Smell | Signal | Technique |
|-------|--------|-----------|
| Feature Envy | a function uses another module's data more than its own | Move Function, Extract then Move |
| Message Chains | `a.b().c().d()` | Hide Delegate, Extract Function |
| Middle Man | a class mostly delegates | Remove Middle Man, Inline Function |
| Inappropriate Intimacy / Insider Trading | modules reach into each other's internals | Move Function and Field, Hide Delegate |

## Data and control

| Smell | Signal | Technique |
|-------|--------|-----------|
| Global Data | a global read and written everywhere | Encapsulate Variable |
| Mutable Data | state changed in distant places | Encapsulate Variable, Split Variable, Replace Derived Variable with Query, immutability |
| Repeated Switches | the same type test in several places | Replace Conditional with Polymorphism, Strategy |
| Flag Argument | a boolean that selects behavior | Remove Flag Argument |
| Deep Nesting | arrow-shaped code | Replace Nested Conditional with Guard Clauses |
| Loops | manual loops for filter, map or reduce | Replace Loop with Pipeline |
| Data Class | fields and accessors only | Move behavior in, Encapsulate Record |
| Refused Bequest | a subclass ignores what it inherits | Replace Subclass with Delegate, Push Down |
| Alternative Classes with Different Interfaces | two classes do the same job | Change Function Declaration, Extract Superclass |
| God object / module | one unit knows and does everything | Extract Class, then report if structural |

## Test smells (the Refactor step applies to tests too)

| Smell | Signal | Technique |
|-------|--------|-----------|
| Fragile test | breaks when unrelated code changes | assert behavior, not internals; remove mock over-specification |
| Mystery Guest | the test depends on data defined elsewhere | inline the data or name a fixture for it |
| Eager test | one test checks many behaviors | split into one behavior per test |
| Obscure test | cannot tell what is being verified | rename, Arrange-Act-Assert layout, named helpers |
| Test code duplication | the same setup pasted everywhere | extract a fixture or builder |
| Slow or order-dependent test | shared state, real I/O | isolate state, fake the boundary |
| Assertion roulette | many bare asserts, no message | one outcome per test, descriptive names |

## Language-specific smells

See the file of the language in `stacks/` (for example unquoted variables in shell, mutable default arguments in Python, `unwrap` in Rust libraries).
