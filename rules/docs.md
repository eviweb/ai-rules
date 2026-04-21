# Documentation

Every project must include the following files from the start:

- `README.md` — project description, usage, install instructions
- `CHANGELOG.md` — updated on every meaningful change
- `VERSION` — single line, semver (e.g. `1.0.0`), source of truth for version numbers
- `LICENSE.md` — ask the user to validate the license choice before creating it
- `TODO.md` — task tracker, structured by phases and themes (see below)

Keep all documentation up to date as the project evolves.

## Keep docs in sync with the code

Update documentation **in the same commit** as the code change that affects it — never defer doc updates to a separate pass:

| Change type | Documents to update |
|---|---|
| New feature or command | `README.md` (usage, examples), `CHANGELOG.md` (`[Unreleased]` → Added), `TODO.md` (mark done or add new tasks) |
| Behaviour change | `README.md` (affected sections), `CHANGELOG.md` (`[Unreleased]` → Changed) |
| Bug fix | `CHANGELOG.md` (`[Unreleased]` → Fixed) |
| Breaking change | `README.md` (migration notes), `CHANGELOG.md` (`[Unreleased]` → Changed or Removed), `VERSION` bump |
| New environment variable or config key | `.env.example`, `README.md` (configuration section) |
| Dependency added or removed | `README.md` (requirements section if user-facing) |

Rules:
- A commit that adds or changes observable behaviour without updating `README.md` and `CHANGELOG.md` is incomplete
- `TODO.md` must reflect the current state of the work: mark tasks done as soon as they are, add new tasks as soon as they are identified
- Do not batch doc updates into a dedicated "docs" commit at the end of a session — keep them co-located with the code they describe

## TODO.md structure

`TODO.md` is the project's task tracker. It must be kept up to date alongside the code.

Structure:
```
# TODO

## Phase 1 — <name>
### <Theme>
- [ ] Task
- [x] Done task

## Phase 2 — <name>
...

---

## Future / Postponed
Items planned for a later phase, intentionally deferred.
- [ ] ...

## Deferred / Under Consideration
Ideas not yet committed to — may or may not happen.
- [ ] ...
```

Rules:
- Phases reflect the project's delivery roadmap; themes group related tasks within a phase
- "Future / Postponed" comes before "Deferred / Under Consideration": postponed items are more concrete (scoped but delayed), whereas under-consideration items are still exploratory
- Completed tasks (`[x]`) may be kept for traceability or removed — be consistent
- Add a separator (`---`) before the two trailing sections to visually distinguish backlog from active work

## Private directory

Every project must include a `.private/` directory and a `.gitignore` at the root.

Create `.private/` at project start — it holds local notes, draft messages, and
sensitive context that must never be committed.

The `.gitignore` must include at minimum:

```gitignore
# Private local directory
.private/

# Secrets and credentials
.env
.env.*
!.env.example
*.key
*.pem
*_token
*_secret

# OS artifacts
.DS_Store
Thumbs.db

# Editors
.idea/
.vscode/
*.swp
*.swo
*~

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
dist/
build/
*.egg-info/

# Node
node_modules/
npm-debug.log*

# Logs
*.log
logs/
```

Adapt to the project's language stack — add entries as needed, never remove the `.private/` entry.

## Community / open source (on user request)

When the user intends to share the project publicly, propose the following files and wait for explicit validation before creating each one:

- `CONTRIBUTING.md` — contribution guidelines (workflow, conventions, PR process)
- `CODE_OF_CONDUCT.md` — code of conduct (e.g. Contributor Covenant)
- `SECURITY.md` — vulnerability reporting policy
- `SUPPORT.md` — where to get help
- `.github/ISSUE_TEMPLATE/bug_report.md` — bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` — pull request template
- `AUTHORS.md` — list of contributors (optional, ask user)

The application/script must read its version from the `VERSION` file, not from a hardcoded constant.

**First commit of a new project:** `init: <short message>` with a detail block.
**Subsequent commits:** standard conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, etc.).
