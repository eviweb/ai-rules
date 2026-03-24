# Test-Driven Development

Always apply TDD. At the start of a project, propose one or more suitable test frameworks with a clear recommendation. Use the framework validated by the user throughout the project.

- Follow the Red-Green-Refactor cycle: write a failing test first, make it pass with minimal code, then refactor.
- Write tests before or alongside every new feature or fix.
- Keep tests in a `tests/` directory with a dedicated runner script.
- For shell scripts: bats-core is the standard choice.
