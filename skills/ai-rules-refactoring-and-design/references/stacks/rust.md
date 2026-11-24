# Rust

## Idioms
- Let ownership guide the design: borrow before cloning; `Result` and `?`; custom error enums (`thiserror` in libraries).
- Newtypes and enums to make illegal states unrepresentable; `From` and `TryFrom` for conversions; builders for many options.
- Iterators over index loops; `#[must_use]`; traits for behavior, generics when static dispatch matters.

## Signals
- `unwrap` or `expect` in library code, needless `clone`, stringly typed values, `Rc<RefCell<_>>` used to dodge the borrow checker.
- Lifetime contortions (often a sign the data should be owned or the design split), `unsafe` without a documented invariant, enums with dozens of variants.

## Detectors
- `cargo clippy` (default lints; `-W clippy::pedantic` on request), `cargo fmt`, `cargo test` or `cargo nextest`.
- `cargo machete` or `cargo udeps` (unused dependencies), `cargo deny` and `cargo audit` (licenses, advisories), `cargo geiger` (unsafe).
- `cargo mutants` (mutation testing); `rust-analyzer` for rename, extract and inline.
