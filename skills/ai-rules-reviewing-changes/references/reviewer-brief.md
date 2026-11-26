# Reviewer brief

Use this brief for a review against the intent: as the author doing a separate review pass, or handed with the package to another session, agent or person. The reviewer gets the package, the spec or plan path and this brief, never the conversation that produced the change.

## Inputs

- **What was built**: two or three sentences.
- **Requirements**: the spec or plan path, and its review focus if it has one (the inputs and failure modes no test exercises; check each one deliberately).
- **Package**: the file written by `scripts/review-package.sh`.

## Rules for the reviewer

- **Read-only.** Do not change the working tree, the index or the branch. Use the package, `git show` and `git log`.
- **The spec is a vision, not an inventory.** Where it is silent, judge by what a reasonable user would expect; grade by the effect on that user, not by whether the spec names the case.
- **Only what you read.** No finding on code you did not read; no "looks good" without checking.

## What to check

- **Alignment**: does the change do what the spec or plan asks, all of it and nothing more? Are deviations justified? Is the plan itself wrong somewhere?
- **Correctness**: logic, edge cases, error handling, input validation, resource cleanup.
- **Design**: simple, readable, cohesive; no speculative abstraction; fits the surrounding code (`ai-rules-refactoring-and-design`).
- **Tests**: real behavior rather than mocks, edge cases, a test that failed first for each fix.
- **Security and privacy**: secrets, injection, permissions, personal data.
- **Production readiness**: compatibility, migrations, docs and changelog, operability.

## Output

```markdown
### Findings

#### Blocking
1. **<title>** — `path/to/file.py:42`
   What is wrong, why it matters for a user, how to fix it (if not obvious).

#### Important
…

#### Minor
…

### Declined to judge
One line per behavior considered and set aside as out of scope, with the reason. Empty means nothing was set aside.

### Verdict
Ready to commit: yes, no, or with fixes. One or two sentences of reasoning.
```

Grading:

- **Blocking**: wrong results, data loss, a security hole, a broken build or test, a spec requirement not met.
- **Important**: a likely bug on a realistic input, a missing test for new behavior, poor error handling, a design that will make the next change hard, outdated docs.
- **Minor**: style, naming, small simplifications, polish.

Be specific (file and line), explain why each finding matters, do not grade a nitpick as blocking, and always give a verdict.
