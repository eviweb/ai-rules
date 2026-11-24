# Correctness
The system does what was asked, completely and precisely, and solves the user's real problem.

- Write the requirements with acceptance criteria before building; derive the first tests from them
- Completeness: every stated requirement is implemented and traceable to a test
- Correctness: results are right, including edge cases, units, time zones and rounding
- Appropriateness: check the stated need against the underlying goal; ask when they differ
- Keep documentation and behaviour in agreement

Red flags: requirements without tests, features nobody asked for, behaviour that contradicts the docs, "works on my example" as the only evidence.
