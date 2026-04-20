# Continuous Integration

## Setup
- Workflow files:
  - Forgejo: `.forgejo/workflows/`
  - GitHub: `.github/workflows/`
- Propose the CI structure at project start and wait for user validation before creating it
- Add a CI status badge to `README.md` once the workflow is in place

## Triggers
- Run on `push` and `pull_request`

## Jobs
- **lint** — run `shellcheck` on all shell scripts
- **test** — run the bats-core test suite
- **build** — run if the project produces build artifacts

## Rules
- Fail fast on error
- Never hardcode secrets in workflow files — use platform secrets (Forgejo variables/secrets or GitHub Actions secrets)

## Job timeouts

Set explicit timeouts on every job to prevent runaway builds from consuming minutes/credits:

| Job type | Recommended timeout |
|----------|-------------------|
| lint | 5 min |
| unit tests | 15 min |
| integration tests | 30 min |
| build | 20 min |
| deploy | 15 min |

```yaml
jobs:
  test:
    timeout-minutes: 15
```

Default to the shortest reasonable value — increase only when a job consistently needs more.

## Caching strategies

Cache dependency installs to avoid re-downloading on every run. Always key on the lockfile so the cache is invalidated when dependencies change.

### Python (uv / pip)
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
    restore-keys: uv-${{ runner.os }}-
```

### Node.js (npm)
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
    restore-keys: npm-${{ runner.os }}-
```

### Node.js (pnpm)
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.local/share/pnpm/store
    key: pnpm-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
    restore-keys: pnpm-${{ runner.os }}-
```

### Rust (cargo)
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target/
    key: cargo-${{ runner.os }}-${{ hashFiles('Cargo.lock') }}
    restore-keys: cargo-${{ runner.os }}-
```

Rules:
- Always use a lockfile as the cache key hash — never hash `package.json` or `pyproject.toml` alone
- Add a `restore-keys` fallback so partial cache hits still save time
- Never cache build outputs that contain secrets or environment-specific paths

## Artifact retention

Attach artifacts only when they provide diagnostic or release value. Set short retention for ephemeral artifacts.

| Artifact type | Retention |
|---------------|-----------|
| Test reports / coverage | 7 days |
| Build artifacts (non-release) | 7 days |
| Release artifacts | 90 days (or keep via platform release) |

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-report
    path: reports/
    retention-days: 7
```

- Do not upload artifacts on every push — scope uploads to relevant branches (`main`, release branches) or failure conditions
- Always name artifacts explicitly — avoid generic names like `output` or `build`
