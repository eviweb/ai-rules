# Testing

Complements `rules/tdd.md` (which mandates TDD and the Red-Green-Refactor cycle). This file covers test structure, naming, coverage, and per-language conventions.

## Test pyramid

Write tests at the right level — don't over-invest in any single layer:

```
        /\
       /  \   E2E / integration (few, slow, high confidence)
      /----\
     /      \  Integration / contract (moderate)
    /--------\
   /          \ Unit (many, fast, isolated)
  /____________\
```

- **Unit tests**: test one function or class in isolation, no I/O, no network, no filesystem
- **Integration tests**: test the interaction between components (DB, HTTP, filesystem)
- **E2E tests**: test the full system from the user's perspective — keep these few and focused on critical paths

Rule: if a unit test requires mocking more than 2–3 dependencies, it is probably an integration test in disguise — restructure accordingly.

## Naming conventions

Test names must describe the scenario and expected outcome, not the implementation:

```
test_<unit>_<scenario>_<expected_outcome>
```

Examples:
- `test_parse_arguments_missing_flag_raises_error`
- `test_install_agent_dry_run_makes_no_changes`
- `test_generate_flat_file_overwrites_existing`

Avoid:
- `test_1`, `test_foo`, `testMethod` — meaningless
- `test_parse_arguments` alone — describes what, not when and what outcome

For bats (shell):
```bash
@test "install: dry run does not create symlink" { ... }
@test "generate: overwrites existing flat file" { ... }
```

## Test structure — Arrange / Act / Assert

Every test must follow the AAA pattern with a clear separation:

```python
def test_install_agent_backs_up_existing_file(repo_root, install_dir):
    # Arrange
    existing = install_dir / "entry.md"
    existing.write_text("old content")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])

    # Act
    actions = install_agent(repo_root, agent)

    # Assert
    assert any("BACKUP" in a for a in actions)
    assert (install_dir / "entry.md").is_symlink()
```

- One assertion per logical outcome — multiple `assert` calls are fine if they verify the same behaviour
- Never assert implementation details (internal calls, private state) — assert observable outcomes

## Coverage

- Minimum threshold: **80%** line coverage for application code
- Target **100%** for critical paths (auth, data validation, financial logic)
- Coverage is a floor, not a goal — 80% with meaningful tests beats 100% with trivial ones
- Exclude from coverage: migration files, generated code, `__main__` blocks, vendored code
- Configure thresholds in the project config and enforce in CI:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-fail-under=80"
```

## Test data and fixtures

- Use fixtures for shared setup — avoid duplicating setup code across tests
- Keep fixtures minimal: set up only what the test needs
- Prefer in-memory or temporary filesystem fixtures over real external systems in unit tests
- Name fixtures after the object they represent, not their role: `repo_root`, `agent`, not `setup`, `ctx`
- Never share mutable state between tests — each test must be fully independent

## Per-language conventions

### Python (pytest)
- One test file per module: `src/ai_rules/installer.py` → `tests/test_installer.py`
- Use `pytest.fixture` for setup; use `tmp_path` for temporary filesystem operations
- Parametrize repetitive cases with `@pytest.mark.parametrize`
- Mark slow or integration tests with `@pytest.mark.slow` and skip in fast runs

### Shell (bats-core)
- One `.bats` file per script under test
- Use `setup()` and `teardown()` for test isolation
- Use `bats-support` and `bats-assert` for readable assertions:
  ```bash
  load 'bats-support/load'
  load 'bats-assert/load'

  @test "script exits 0 on success" {
    run ./my-script.sh
    assert_success
  }
  ```

### JavaScript / TypeScript (Jest / Vitest)
- One test file per module: `src/auth.ts` → `src/auth.test.ts` or `tests/auth.test.ts`
- Use `describe` blocks to group related tests; `it` / `test` for individual cases
- Use `beforeEach` / `afterEach` for setup/teardown — never `beforeAll` for mutable state
- Mock external modules at the module boundary, not deep inside implementation code

### Go
- Test files alongside source: `config.go` → `config_test.go`
- Use table-driven tests for multiple input/output combinations:
  ```go
  tests := []struct {
      name  string
      input string
      want  string
  }{
      {"empty input", "", ""},
      {"valid value", "foo", "foo"},
  }
  for _, tt := range tests {
      t.Run(tt.name, func(t *testing.T) {
          got := process(tt.input)
          if got != tt.want {
              t.Errorf("got %q, want %q", got, tt.want)
          }
      })
  }
  ```
- Use `t.Helper()` in helper functions to get accurate failure line numbers
- Prefer `testify/assert` over raw `t.Error` for readability
