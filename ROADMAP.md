# ai-rules — Roadmap: from static rules to an on-demand, process-aware system

> Status: draft, tracked in the repo since 0.6.2 work — target versions 0.6.2 → 1.0.0
> Tracker: `TODO.md` mirrors the phases below as checklists (phase names prefixed `R`)
> Baseline: ai-rules 0.6.1 (25 imported rule files, 110 tests, 94.65 % coverage)
> Inspiration: [obra/superpowers](https://github.com/obra/superpowers) (MIT) — mechanisms only, not its methodology as-is

---

## 1. Goals

Keep ai-rules as the single source of truth for personal engineering standards, and adopt the
runtime mechanisms that make Superpowers efficient:

1. **Small always-on core, everything else on demand** — cut the per-session context cost.
2. **Procedures that trigger themselves** — turn passive rules into skills the agent invokes at the right moment.
3. **Enforcement where it matters** — hooks and permissions back up the rules that must never be broken.
4. **Measured, not assumed** — token budgets and behavior checks enforced in CI.
5. **Cross-agent parity preserved** — Claude Code first, Codex and Antigravity kept in sync through generation.

### Non-goals

- Installing Superpowers alongside ai-rules (conflicting commit, merge and autonomy policies).
- Replicating the full Superpowers pipeline (visual companion, telemetry, multi-hour autonomous runs).
- Supporting new agents (Cursor, Copilot, Windsurf) before the skills layer is stable.

### Guiding principles

- Every rule must answer: *when is it needed?* → always (core), for some files (scoped), for some tasks (skill).
- Adapt, don't copy: every imported Superpowers mechanism must comply with `principles.md`, `commits.md` and `git.md`.
- Any change to rule content is validated against a before/after behavior check (see Phase 7).

---

## 2. Findings addressed

| # | Finding | Evidence | Phase |
|---|---------|----------|-------|
| F1 | Heavy always-on context | 25 files, ~65 KB (~24.5k tokens, measured with `/context` on 2026-11-19, see `docs/metrics/baseline-0.6.1.md`) loaded in every session; Codex flat file 1,544 lines, needs `project_doc_max_bytes = 131072` | 0, 2 |
| F2 | Overlapping loading paths | Claude Code auto-loads `~/.claude/rules/*.md` at launch **and** `CLAUDE.md` `@imports` the same files. Measured (`/context`, 2026-11-19, two runs): with the symlink deployment, the only mode `ai-rules install` creates, both resolve to the same real paths and each file is loaded once, so there is no double cost (a copied deployment was not tested). The real cost was a non-imported file (`ci-triggers-template.md`, ~2.4k tokens) loaded anyway because the whole directory is auto-loaded: fixed in 0.6.2 | 0 |
| F3 | `settings.json` symlinked and over-permissive | Claude Code writes into the repo (plugins, `/permissions`); `rm -fr`, `rm -r -f`, `git push --force`, `git checkout -- .`, `npx *` allowed; `git commit *` / `git push *` auto-allowed despite "never commit autonomously"; `autoApprove` key unverified | 1, 5 |
| F4 | No activation mechanism | Rules state *what* (TDD mandatory, propose before implementing) but nothing triggers *how* at the right time; only the commit hook enforces anything | 3, 4, 5 |
| F5 | Agent-specific and context-blind wording | "Claude Code commit workflow" inside a rule shared with Codex/Gemini; "TDD, no exceptions" ill-suited to config/infra work | 8 |
| F6 | No measurement of rule effectiveness | Integrity tests check structure, not agent behavior or size budgets | 7 |

---

## 3. Target architecture

```
ai-rules/
├── core/                         # ALWAYS LOADED — hard budget ≤ 200 lines, ≤ 10 KB total
│   ├── language.md
│   ├── principles.md
│   ├── security.md               # condensed: secrets, permissions, least privilege
│   ├── commits.md                # commit gate only (agent-neutral)
│   └── git.md                    # profile + branch/merge essentials
├── rules/                        # SCOPED — loaded only when matching files are touched
│   ├── shell.md                  # paths: ["**/*.sh", "**/*.bash", "bin/**"]
│   ├── api.md                    # paths: ["**/api/**", "**/routes/**", "openapi*.{yml,yaml,json}"]
│   ├── ci.md                     # paths: [".github/workflows/**", ".forgejo/workflows/**"]
│   └── ...
├── skills/                       # ON DEMAND — procedures invoked by task type
│   ├── using-ai-rules/           # bootstrap, injected at session start
│   ├── brainstorming/
│   ├── writing-plans/
│   ├── executing-plans/
│   ├── subagent-execution/       # optional, opt-in
│   ├── test-driven-development/
│   ├── systematic-debugging/
│   ├── verification-before-completion/
│   ├── requesting-code-review/
│   ├── receiving-code-review/
│   ├── finishing-a-branch/
│   ├── releasing/                # from release.md + changelog.md + versioning.md
│   ├── designing-an-api/         # from api.md (full reference)
│   ├── hardening-ci/             # from ci.md + templates/ci-triggers.md
│   └── writing-rules-and-skills/ # meta: how to author/test ai-rules content
├── hooks/
│   ├── session-start             # injects using-ai-rules on startup|clear|compact
│   └── pre-tool-guard            # blocks destructive commands, gates commit/push
├── settings/
│   └── claude.fragment.json      # keys owned by ai-rules, merged (not symlinked)
├── agents/
│   ├── claude/CLAUDE.md          # imports core/ only
│   ├── codex/AGENTS.md           # generated: core only; skills native via ~/.agents/skills
│   └── antigravity/rules/        # generated: modular rules with trigger frontmatter
└── agents.toml                   # new link types: skills, hooks, settings_merge
```

### Loading model

| Layer | Loaded when | Budget | Mechanism (Claude Code) |
|-------|-------------|--------|-------------------------|
| Core | Every session | ≤ 200 lines / ≤ 10 KB | `@core/*.md` from `CLAUDE.md` |
| Bootstrap | Every session, re-injected after compaction | ≤ 3 KB | `SessionStart` hook, matcher `startup\|clear\|compact` |
| Scoped rules | Agent reads a matching file | ≤ 6 KB each | `~/.claude/rules/*.md` with `paths:` frontmatter |
| Skills | Task matches the skill description | `SKILL.md` ≤ 8 KB; long references in sibling files | `~/.claude/skills/<name>/SKILL.md` |
| Skill references | Explicitly requested by the skill | unbounded, read on demand | Files next to `SKILL.md` |

Expected outcome: always-on context drops from ~65 KB to ≤ 13 KB (core + bootstrap), i.e. roughly −80 %.

---

## 4. Phases

### Phase 0 — Baseline and loading hygiene (0.6.2)

**Goal:** measure before changing anything; remove the free win.

- [x] Integrate this roadmap into the repository (`ROADMAP.md`) and align `TODO.md` with it
- [x] Record baseline with `/context` and `/memory` in a fresh Claude Code session: total memory tokens, list of loaded rule files (`docs/metrics/baseline-0.6.1.md`; `/memory` returned no data, filesystem inspection used)
- [x] Add `scripts/measure-context.sh`: byte/line/approx-token counts for every layer (core, scoped, skills, flat files); output as Markdown table
- [x] F2 settled by measurement: the symlink deployment loads each file once, so the two options considered are dropped
  - Option A (deploy to `~/.claude/ai-rules/rules`, not auto-loaded): saves only the template, and disables the auto-load that Phase 3 relies on for `paths:` scoping
  - Option B (remove the `@rules/` imports): saves almost nothing (`CLAUDE.md` is ~0.3k tokens) and breaks the Codex flat file, which is generated by resolving those imports
- [x] Ensure experimental files are never auto-loaded (`ci-triggers-template.md` moved to `templates/ci-triggers.md`)
- [x] Integrity test: every `rules/` file is imported by `CLAUDE.md` (`rules/` is auto-loaded, so a non-imported file would be loaded unnoticed) — `tests/test_rules_integrity.py`
- [x] Document the effective loading mechanism in `README.md`

**Acceptance (met):** `/context` shows each rule exactly once and `ci-triggers-template.md` absent from loaded memory (second run, 2026-11-19: memory files 27.3k → 24.9k tokens); baseline numbers committed in `docs/metrics/baseline-0.6.1.md`.

---

### Phase 1 — Settings hardening (0.6.3)

**Goal:** stop writing into the repo, close permission holes, align permissions with `commits.md`.

- [x] Replace the `settings.json` symlink with a **managed merge**: generalize the existing `config_patches` mechanism (TOML, Codex) to JSON
  - `agents.toml`: new `[[agents.claude.settings_merge]]` entries listing owned key paths (`permissions.allow`, `permissions.deny`, `permissions.ask`, `hooks`)
  - Track owned entries in `$XDG_STATE_HOME/ai-rules/state/claude-settings.json` so `remove` reverts only what ai-rules added
  - Never overwrite keys Claude Code manages (`enabledPlugins`, model, theme…)
- [x] Move to `ask`: `git commit *`, `git push *`, `rm *`, `npx *`, `chmod *`
- [x] Extend `deny`: `rm -fr *`, `rm -r *`, `rm -R *`, `git push --force *`, `git push -f *` (a space before `*` leaves `--force-with-lease` under `ask`, as allowed by `git.md`), `git reset --hard *`, `git checkout -- *`, `git clean *`, `git branch -D *`
- [x] Remove `autoApprove` unless confirmed in current Claude Code settings documentation
- [x] Migration in `update`: detect legacy symlink, back it up to XDG state, replace with a regular file containing merged content
- [x] Tests: merge idempotency, removal restores pre-install content, unknown user keys preserved

**Acceptance:** installing a plugin or editing `/permissions` leaves the ai-rules working tree clean; `ai-rules remove` restores the exact previous `~/.claude/settings.json`.

> Note: permission patterns are prefix-based and remain bypassable (`bash -c`, `sh -c`, `xargs rm`). Phase 5 adds a parsing guard hook as the real safeguard.

---

### Phase 2 — Skills infrastructure and transition skills (0.7.0)

**Goal:** make skills a first-class, deployable, testable unit, and give the rules that Phase 3 will take out of the always-on context a home that exists first. Reordered before core slimming (decision 2026-11-23): moving rules out of the always-on context before skills exist would leave `release`, `pr`, `review`, `issues` and `quality` unloaded.

- [x] `agents.toml`: new link type `skill_dirs` (directory of skill folders → `<install_dir>/<target>/<name>`), one symlink per skill so user-authored skills coexist; `update` prunes deleted skills, `remove` unlinks only ai-rules skills
- [x] Skill format (Agent Skills convention): `SKILL.md` with YAML frontmatter `name`, `description`; optional `references/`, `scripts/`; strict frontmatter parser, no YAML dependency (`docs/skills.md`)
- [x] Description style guide: start with the trigger ("Use when…"), name the task types, ≤ 300 characters; descriptions are the only part always visible, so they carry the activation logic
- [x] `ai-rules skills list|status|verify` subcommands
- [x] Integrity tests (`tests/test_skills.py`, `tests/test_skills_integrity.py`):
  - frontmatter present and valid; `name` matches folder
  - `SKILL.md` ≤ 8 KB
  - every referenced sibling file exists; scripts are executable and pass `shellcheck`
- [ ] Integrity test: no skill duplicates core content (heuristic: shared headings): moved to Phase 3, since `core/` does not exist yet and the transition skills duplicate loaded rules on purpose
- [x] Codex: native skills — each skill is a symlink into `~/.agents/skills/ai-rules-<name>/` (Codex follows symlinked skill folders); no skill index needed in the flat file; confirmed in Codex (`/skills`, `$ai-rules` filter)
  - [x] Keep descriptions ≤ 300 characters: the initial skills list is capped at 2 % of the context window (8,000 characters if unknown) and descriptions are shortened first
  - [ ] Optional `agents/openai.yaml` per skill: set `policy.allow_implicit_invocation: false` for manual-only skills (e.g. `releasing`): with the first manual-only skill (Phase 4)
- [ ] Antigravity: native skills — deploy to `~/.gemini/config/skills/ai-rules-<name>/` (see Phase 6)
- [x] Namespace all skills: folder and `name` carry the `ai-rules-` prefix (enforced by `skills verify`); plugin skills are namespaced by Claude Code anyway, the prefix protects against same-named personal or project skills
- [x] **Transition skills**: port existing rules as skills, wording unchanged (no rewrite), so Phase 3 can unload them without a behavior gap; a parity test keeps each skill identical to its rule while both exist:
  - `ai-rules-starting-a-project` (from `editor`, project-start parts of `docs` and `security`: `.editorconfig`, mandatory files, `.gitignore`; a `paths:` rule cannot trigger on a missing file)
  - `ai-rules-quality-dimensions` (from `quality`; the full text is in `references/dimensions/`, one file per dimension, because `quality.md` exceeds the 8 KB limit of a `SKILL.md`)
  - `ai-rules-reviewing-changes` (from `review`)
  - `ai-rules-pull-requests-and-issues` (from `pr`, `issues`)
- [ ] Skills index in `CLAUDE.md` (3–5 lines naming each skill with its trigger): moved to Phase 3, when the rules are unloaded; redundant with the automatic skill listing while they are loaded, and it would leak into the Codex flat file before the generator handles skills

**Known cost until Phase 3:** the transition skills duplicate rules that are still loaded at launch. The listing costs about 0.3k tokens (measured, `docs/metrics/0.7.0.md`); invoking a skill adds its text on top of the same text already in context (worst case `ai-rules-quality-dimensions` with its reference, about +3.2k). Accepted for the additive 0.7.0, bounded to the 0.7.0 → 0.8.0 window and guarded by the parity test.

**Acceptance:** `ai-rules install claude` deploys skills; `/skills` (or equivalent) lists them; `remove` cleans only ai-rules skills; the four transition skills reproduce the content of the rules they come from (no text change). (met for Claude Code and Codex; Antigravity follows in Phase 6).

---

### Phase 3 — Core slimming and scoped rules (0.8.0)

**Goal:** split rules by *when they are needed*.

- [x] Classify each of the 25 files (see Appendix A for the proposed mapping)
- [x] Create `core/` with condensed, imperative versions of: `language`, `principles`, `security` (essentials), `commits` (gate only), `git` (profile + merge policy)
- [x] Add `paths:` frontmatter to file-type rules (`shell`, `ci`, `api`, `logging`, `error-handling`, `naming`, `editor`, `testing`)
- [x] Unload task-type material now hosted by skills: `review`, `pr`, `issues`, `quality` (Phase 2 transition skills), and later the Phase 4 skills (`release`, `changelog`, `versioning`, `docs`, `dependencies`, `compatibility` stay path-scoped until then)
- [x] Targeted condensation, only what `core/` needs to meet its budget (`git`, `security`, `commits` gate): the six core candidates weigh 11.5 KB against a 10 KB budget. No global rewrite of the other rules: they load on demand, so the saving is small and the risk of changing a rule's meaning is not worth it (decision 2026-11-23). Guard: an invariants test lists the normative statements of the core (e.g. never commit autonomously, propose before implementing, English only) and fails when one disappears; the removed rationale stays in git history and, where useful, in a skill reference
- [ ] Split `naming`, `error-handling`, `logging` by language only if the measured saving justifies it (separate PR, after the classification)
- [x] Skills index in `CLAUDE.md` (3–5 lines naming each skill with its trigger), moved from Phase 2, until the Phase 5 bootstrap hook injects it
- [x] Generator: Codex flat file = core + scoped rules inlined with an "Applies when working on" note (the skill index is not inlined: Codex lists its native skills); Gemini, which has no skills, gets the same plus the skill texts. Both come from templates (`flat_source`)
- [x] CI size budgets (new tests in `test_rules_integrity.py`):
  - core ≤ 200 lines and ≤ 10 KB
  - each scoped rule ≤ 6 KB
  - every non-core rule has `paths:` frontmatter or lives under `skills/`
  - no skill duplicates core content (heuristic: shared headings), moved from Phase 2

**Acceptance (met, `docs/metrics/0.8.0.md`):** `/context` no longer lists `review`, `pr`, `issues` and `quality` as memory files; memory files drop from 25k to 3.7k tokens (`CLAUDE.md` + core 3.5k, the rest is the auto-memory index); always-on size 9.5 KB of core (≤ 10 KB, before bootstrap); Codex flat file ≤ 32 KB, `project_doc_max_bytes` patch no longer required (**not met in 0.8.0**: core plus scoped rules inlined make 54 KB, the patch stays; reducing it needs Codex-specific condensation or an index with on-demand reads, Phase 6); behavior checks from Phase 7 show no regression on the 3 reference tasks.

---

### Phase 4 — Process skills adapted from Superpowers (0.9.0)

**Goal:** bring the *how* — adapted to ai-rules policies.

Adaptation rules applying to every skill below:

- **Commit gate preserved:** no skill commits. At each checkpoint the skill writes `.private/COMMIT_MESSAGE` and asks for explicit approval (`commits.md`).
- **Propose before implementing preserved:** design and plan approval are explicit gates.
- **Merge policy preserved:** branch completion follows the project profile (`git.md`): strict → PR + merge commit; light → PR recommended, direct commit tolerated for trivial changes.
- **Agent-neutral wording;** Claude-specific tool names only in a "Claude Code notes" section.
- **Attribution:** root `THIRD_PARTY.md` crediting obra/superpowers (MIT, with the license text) for adapted skills, upstream version pinned in `derived-from` (v7.0.2, `22f0b46`); skills are rewritten, never copied; each adapted `SKILL.md` carries a `derived-from:` frontmatter field.

| Skill | Source | Adaptation |
|-------|--------|------------|
| `using-ai-rules` | `using-superpowers` | Bootstrap: lists skills, states "check for a matching skill before acting", reminds the commit gate; ≤ 3 KB |
| `brainstorming` | `brainstorming` | Keep question-first flow and chunked design playback; small changes agreed in chat, larger ones produce `docs/design/<topic>.md`; skip for ops one-liners |
| `writing-plans` | `writing-plans` | 2–5 min tasks, exact paths, verification step per task; **word budget** per task (Superpowers v6 cut test content ~62 %); plan stored in `.private/plans/` (untracked) unless the user asks otherwise |
| `executing-plans` | `executing-plans` | **Default execution mode** (inline, cheapest); checkpoint every N tasks with commit proposal; final self-review |
| `subagent-execution` | `subagent-driven-development` | **Opt-in only.** Adopt: task brief written to a file (no pasting through controller context), single combined reviewer (spec + quality), review package script, explicit **model tiering** (cheap for mechanical 1–2 file tasks, standard for integration, top tier for design/review of risky diffs); subagents never commit |
| `test-driven-development` | `test-driven-development` | Red-green-refactor kept; **scope clause**: applies to code with testable behavior; config/infra changes use `verification-before-completion` instead (dry-run, `--check`, `nginx -t`, `haproxy -c`, `postfix check`…); "delete code written before tests" replaced by "propose to rewrite test-first" |
| `systematic-debugging` | `systematic-debugging` | Taken nearly as-is (root cause before fix, 4 phases); add infra examples (DNS, proxies, containers) |
| `verification-before-completion` | `verification-before-completion` | Evidence before "done": command output shown, not claimed; infra variant with syntax checks and service status |
| `requesting-code-review` | `requesting-code-review` | Self-review using `review.md` checklists (content moved here); `review-package` script generating diff + stat + plan excerpt to `.private/review/` |
| `receiving-code-review` | `receiving-code-review` | Verify each suggestion against the code before applying; no performative agreement |
| `finishing-a-branch` | `finishing-a-development-branch` | Options driven by project profile; PR via `gh`/`tea`/`fj` (Forgejo) with merge commit; branch deletion per `git.md` |
| `releasing` | — | From `release.md` + `changelog.md` + `versioning.md`: bump only in release commit, `VERSION` single source |
| `writing-rules-and-skills` | `writing-skills` | How to author/condense ai-rules content; mandatory before/after behavior check (Phase 7) |

Explicitly **not** adopted (or deferred):

- Git worktrees by default — kept as an optional section in `subagent-execution` for parallel work only.
- Autonomous multi-hour runs — incompatible with the commit gate.
- Visual brainstorming companion and its telemetry.

**Acceptance:** on the 3 reference tasks (Phase 7), the agent invokes the expected skill without being prompted, never commits without approval, and total tokens per task are ≤ baseline.

**Measured (`docs/metrics/0.9.0.md`):** sixteen skills; always-on `CLAUDE.md` + core 4.2k tokens and skill listing about 1.5k (budget 5 KiB, tested); a skill costs its `SKILL.md` once when invoked (~1.7k for `writing-plans`). The behavior part of the acceptance waits for the Phase 7 reference tasks.

---

### Phase 5 — Hooks: bootstrap and enforcement (0.10.0)

**Goal:** guarantee activation and back critical rules with code.

- [ ] `hooks/session-start` (bash, no forks, PATH-independent — same constraints as Superpowers' hook): inject `using-ai-rules` as additional context
  - Matcher `startup|clear|compact` so the bootstrap survives context compaction
  - Emit only the JSON field the current agent consumes
- [ ] `hooks/pre-tool-guard` (PreToolUse on `Bash`): parse the command (including `bash -c`, `sh -c`, `xargs`, `;`, `&&`, pipes) and
  - block recursive deletes outside the working tree, force-push, `reset --hard`, `clean -fd` without prior confirmation
  - for `git commit`: require `.private/COMMIT_MESSAGE` to exist and match the `-F`/`-m` content
- [ ] Deploy hooks through the Phase 1 settings merge (owned `hooks` entries), never by overwriting user hooks
- [ ] Tests: bats-core suite for both hooks (malicious command variants, JSON output shape, empty PATH)
- [ ] Hook latency budget: ≤ 50 ms per invocation, measured in CI

**Acceptance:** after `/compact`, the bootstrap is present again; the documented bypass variants of `rm -rf` are blocked; no false positive on the 3 reference tasks.

---

### Phase 6 — Cross-agent parity (0.11.0)

**Goal:** keep Codex and Antigravity first-class without carrying Claude's full context.

- [ ] Record per-agent capabilities (instructions, conditional rules, skills, hooks, permissions) in `docs/agents-capabilities.md`

#### Antigravity (replaces Gemini)

- [ ] Replace the `gemini` agent with `antigravity` (Gemini CLI sunset for individual tiers on 2026-06-18; keep `gemini` only behind an opt-in flag for enterprise/API-key users)
  - Stop managing `~/.gemini/GEMINI.md` (written by the Antigravity IDE "+ Global" action)
  - Generate modular global rules into `~/.gemini/config/rules/ai-rules-<name>.md` as regular files (no symlinks), tracked in `$XDG_STATE_HOME/ai-rules/state/antigravity.json` for `remove`
  - Generator maps layers to the required `trigger` frontmatter:
    ```yaml
    ---
    trigger: glob
    description: Shell script conventions (strict mode, shellcheck, traps)
    globs: ["**/*.sh", "**/*.bash", "bin/**", "scripts/**"]
    ---
    ```
    core → `always_on`, scoped rules → `glob` (from `paths:`), on-demand rules → `model_decision`
  - Never rely on `@./file` imports (non-eager in Antigravity); use `@[label](path)` only if inlining is required
  - Deploy skills to `~/.gemini/config/skills/ai-rules-<name>/` after validating Claude-style `SKILL.md` compatibility
  - `verify`: fail if any generated rule exceeds 24,000 bytes or if `always_on` rules exceed the 20,000-token aggregate budget
  - `update`: migrate existing installs (remove legacy `~/.gemini/GEMINI.md` and `~/.gemini/rules` symlinks owned by ai-rules, restore backups)

#### Codex

- [ ] Flat `~/.codex/AGENTS.md` generated from `core/` only (no imports supported, one global file read)
- [ ] Re-check whether `project_doc_max_bytes` applies to the global file (current source applies it to project files only); drop the config patch if confirmed, keep migration in `remove`
- [ ] Generate execution policy `~/.codex/rules/ai-rules.rules` (never touch `default.rules`, written by the TUI) from the same source as the Claude permission lists:
  ```python
  prefix_rule(
      pattern = ["git", "push"],
      decision = "prompt",
      justification = "ai-rules: pushes require explicit approval",
      match = [["git", "push", "origin", "main"]],
  )
  prefix_rule(
      pattern = ["git", "commit"],
      decision = "prompt",
      justification = "ai-rules: commits require explicit approval (commits.md)",
  )
  prefix_rule(
      pattern = ["git", "reset", "--hard"],
      decision = "forbidden",
      justification = "ai-rules: irreversible, confirm manually",
  )
  ```
  - CI: run `codex execpolicy check --pretty --rules agents/codex/ai-rules.rules -- <cmd>` against a fixture list of allowed/blocked commands

#### Shared

- [ ] Single permission source: `permissions.toml` (allow / ask / deny) → generated Claude `settings` fragment + Codex `.rules`; Antigravity when a permission mechanism is documented
- [ ] Generator modes per agent in `agents.toml`: `skills = "native" | "index" | "inline"`
- [ ] Embed a rules version header in generated flat files (ex-TODO) for traceability
- [ ] `verify` extended to skills and scoped-rules outputs for every agent

**Acceptance:** `ai-rules verify` green for Claude, Codex and Antigravity; Codex flat file ≤ 32 KiB; generated Antigravity rules within 24,000 bytes each and 20,000 tokens for `always_on`.

---

### Phase 7 — Evals and measurement (continuous, gate for 1.0.0)

**Goal:** prove that each change improves or preserves behavior at lower cost.

- [ ] `evals/` (kept separate, run manually or on demand — not in the default CI job)
  - 3 reference tasks: (a) small feature in a Python CLI with tests, (b) bug hunt in a shell script, (c) config change on an infra file (HAProxy/Postfix-style, no tests)
  - Scenario pressure tests per skill (adapted from Superpowers `writing-skills`): situations where the agent is tempted to skip the procedure
- [ ] Metrics per run: total tokens (main + subagents), wall-clock, number of approval prompts, rule violations (commit without approval, code before test, unrequested refactor)
- [ ] Results stored in `docs/metrics/<version>.md`; regression threshold: tokens +10 % or any new violation blocks the release
- [ ] CI (default job): size budgets, frontmatter validity, loading-path uniqueness, hook tests

**Acceptance:** 1.0.0 metrics show ≥ 60 % less always-on context than 0.6.1 and zero violations on the reference tasks.

---

### Phase 8 — Wording and consistency cleanup (alongside Phases 2–4)

- [ ] Agent-neutral rules: move "Claude Code commit workflow" into a Claude-specific section of `agents/claude/CLAUDE.md` or the bootstrap skill
- [ ] TDD scope clause in core (`principles.md` or `tdd` skill) to cover config/infra work
- [ ] Remove duplication between `security.md`, `quality.md` and `error-handling.md` (single owner per topic, others link to it)
- [ ] Update `README.md` (structure, loading model, budgets), `CHANGELOG.md`, `TODO.md` (replace done/obsolete items, point to this roadmap)
- [ ] Decide the fate of `templates/ci-triggers.md`: becomes a reference file of the `hardening-ci` skill

---

## 5. Release plan

| Version | Content | Breaking |
|---------|---------|----------|
| 0.6.2 | Phase 0 — baseline, loading hygiene | No |
| 0.6.3 | Phase 1 — settings merge, permission hardening | Yes (settings no longer symlinked; migration automatic) |
| 0.7.0 | Phase 2 — skills infrastructure, transition skills | No |
| 0.8.0 | Phase 3 — core + scoped rules, size budgets | Yes (layout change) |
| 0.9.0 | Phase 4 — process skills | No |
| 0.10.0 | Phase 5 — hooks | No |
| 0.11.0 | Phase 6 — cross-agent parity | Yes (gemini agent replaced by antigravity; migration automatic) |
| 1.0.0 | Phase 7 gate passed, docs complete | — |

Each phase follows the strict profile: one PR per phase item, merge commit, CI green, release commit bumps `VERSION` only.

---

## 6. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skills not triggered (weak descriptions) | Rules silently ignored | Bootstrap skill + trigger-first descriptions + pressure tests |
| Scoped rules missed when files are only listed, not read | Convention drift | Keep critical constraints in core; scoped rules only for detail |
| Hook false positives | Friction, user disables hook | bats test corpus from real sessions; explicit override env var logged to XDG state |
| Settings merge corrupts user config | Broken Claude Code setup | Backup before every write, JSON schema validation, idempotency tests |
| Skills format diverges between agents | Parity loss | Native mode per agent, index/inline fallback, compatibility tests per agent |
| Eval cost | Spend on quota | Small fixed task set, run per minor release only, cheap model where possible |
| Upstream Superpowers evolves | Adapted skills drift | `derived-from:` field with upstream commit; monthly automated check of the pinned commit (`docs/sources.md`, `sources-review.yml`) that opens an issue when upstream has moved |

---

## Appendix A — Proposed classification of current rules

| Current file | Target | Notes |
|--------------|--------|-------|
| `language.md` | core | As-is |
| `principles.md` | core | Condensed; add TDD scope clause |
| `security.md` | core (essentials) + scoped `shell` part | File permissions/input validation → `shell.md` |
| `commits.md` | core (gate) + skill `finishing-a-branch` (format details) | Agent-neutral wording |
| `git.md` | core (profile, merge policy) + skill `finishing-a-branch` (workflows) | |
| `naming.md` | scoped | `paths` per language extension |
| `editor.md` | scoped | `paths: [".editorconfig", "**/*"]` or fold into core if ≤ 10 lines |
| `shell.md` | scoped | `paths: ["**/*.sh", "**/*.bash", "bin/**", "scripts/**"]` |
| `cli.md` | scoped | CLI entry points |
| `logging.md` | scoped | Source files |
| `error-handling.md` | scoped | Source files |
| `api.md` | skill `designing-an-api` | Full table as reference file |
| `testing.md` | skill `test-driven-development` (reference) | |
| `tdd.md` | skill `test-driven-development` | Core keeps one line: "TDD for testable code" |
| `quality.md` | skill `brainstorming` (reference: kickoff dimensions) | Used at project/feature start only |
| `dependencies.md` | skill `releasing` + scoped on manifests | `paths: ["**/package.json", "**/pyproject.toml", "**/Cargo.toml", ...]` |
| `compatibility.md` | scoped | Manifests and CI files |
| `docs.md` | skill `writing-docs` or scoped on `**/*.md` | |
| `changelog.md`, `versioning.md`, `release.md` | skill `releasing` | |
| `issues.md`, `pr.md`, `review.md` | skills `requesting-code-review`, `finishing-a-branch` | |
| `ci.md`, `templates/ci-triggers.md` | skill `hardening-ci` + scoped on workflow files | Template as reference file |

## Appendix B — Superpowers mechanisms: adopt / adapt / reject

| Mechanism | Decision | Rationale |
|-----------|----------|-----------|
| SessionStart bootstrap re-injected after compaction | Adopt | Guarantees activation at minimal cost |
| On-demand skills with trigger-first descriptions | Adopt | Core of the context reduction |
| Fork-free, PATH-independent hook scripts | Adopt | Robustness on Termux and minimal shells |
| Task briefs and review packages written to files | Adopt | Avoids pasting large content through controller context |
| Single combined reviewer (spec + quality) | Adopt | ~15 % saving reported upstream |
| Explicit model tiering for subagents | Adopt (opt-in mode) | Biggest cost lever when subagents are used |
| Plan word budgets, terse reviewer contract | Adopt | Output-token savings |
| Skill size tests, pressure-test evals | Adopt | Prevents regressions and silent bloat |
| Per-task autonomous commits | Reject | Conflicts with commit gate |
| Worktrees by default | Adapt (optional) | Overhead for solo, sequential work |
| Local merge as completion option | Reject under strict profile | PR + merge commit required |
| Multi-hour autonomous execution | Reject | Conflicts with propose-before-implementing |
| Visual companion / telemetry | Reject | Out of scope |
