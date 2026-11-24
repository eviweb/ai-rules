# Refactoring techniques

Names follow Fowler's catalogue. Always: one technique at a time, tests run after each step, no behavior change, a commit boundary proposed per coherent step.

## Everyday

- **Extract Function / Inline Function**: name a block by its intent; inline when the body says more than the name.
- **Extract Variable / Inline Variable**: name a sub-expression; drop a variable that adds nothing.
- **Rename** (variable, function, field): the cheapest and most valuable; use the editor or compiler to rename everywhere.
- **Change Function Declaration**: rename or reshape parameters; use Parallel Change when callers are many.
- **Replace Temp with Query**: turn a temporary into a function so it can be reused.
- **Split Variable**: one variable, one meaning.
- **Slide Statements, Split Loop, Split Phase**: group related code, separate concerns inside a function or between two stages (parse, then compute).

## Organizing data and objects

- **Encapsulate Variable / Record / Collection**: hide direct access behind functions.
- **Replace Primitive with Object**: a value object with its own rules (money, id, range).
- **Introduce Parameter Object, Preserve Whole Object, Combine Functions into Class.**
- **Replace Derived Variable with Query, Change Reference to Value.**
- **Move Function / Field, Extract Class, Inline Class, Hide Delegate, Remove Middle Man.**

## Simplifying conditionals

- **Decompose Conditional, Consolidate Conditional Expression.**
- **Replace Nested Conditional with Guard Clauses**: handle the special cases first and return.
- **Replace Conditional with Polymorphism**: when the same switch appears in several places.
- **Introduce Special Case (Null Object), Introduce Assertion.**

## APIs

- **Separate Query from Modifier, Parameterize Function, Remove Flag Argument, Replace Parameter with Query, Replace Query with Parameter, Remove Setting Method, Replace Constructor with Factory Function.**

## Inheritance

- **Pull Up / Push Down Method and Field, Extract Superclass, Collapse Hierarchy, Replace Type Code with Subclasses, Replace Subclass with Delegate, Replace Superclass with Delegate.** Prefer composition when the "is a" is doubtful.

## Loops and algorithms

- **Replace Loop with Pipeline** (filter, map, reduce), **Substitute Algorithm**, **Remove Dead Code.**

## Large-scale techniques

- **Parallel Change (expand and contract)**: add the new form beside the old, migrate the callers step by step, remove the old. Each step is green and releasable.
- **Branch by Abstraction**: put an interface in front of the part to replace, build the new implementation behind it, switch, delete the old.
- **Strangler Fig**: route new behavior to the new module and grow it until the old one can be removed.
- **Mikado Method**: try the change, note what breaks as a dependency graph, revert, fix the leaves first.
- **Feature flag**: ship the new path switched off, enable it progressively, remove the flag and the old path once proven; a safe way to release a large refactoring.
- **Database schema change** (expand and contract): add the new column or table, write to both, backfill, switch reads, then drop the old one, each as its own migration that can be rolled back.
- **Preparatory refactoring / tidy first**: restructure so the intended change becomes small, in its own commit.

## Legacy code without tests (Feathers)

1. **Characterization test**: call the code, record what it really does (including odd results), assert on that. It documents current behavior; it does not judge it.
2. **Seam**: a place where behavior can be changed without editing the code around it (parameter, subclass, injected collaborator, module boundary). Use it to isolate the code under test.
3. **Sprout Method / Class, Wrap Method / Class**: add new behavior in new tested code beside the untested old code instead of editing it.
4. Golden master for large outputs: save the output of a representative run, compare after each step.

## Protocol

1. Tests green, characterization test added if needed.
2. One technique, smallest step; run the tests; green or revert.
3. Re-read the diff: behavior unchanged, names clear.
4. Commit boundary proposed; never commit without the user.
5. Stop at the end of the agreed scope; report the rest as a proposal (`SKILL.md`).
