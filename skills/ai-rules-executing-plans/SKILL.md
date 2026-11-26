---
name: ai-rules-executing-plans
description: "Use when the user has approved a plan and asked to execute it: work the tasks in order under TDD, record progress and rulings in the plan, stop at each commit point with a commit message, propose a handoff note when the session grows heavy, review the whole branch at the end."
metadata:
  derived-from: "superpowers/executing-plans @ 22f0b46"
  license-of-origin: MIT
---
# Executing plans

The plan did the thinking. Execute it task by task, prove each step with a test you watched fail and then pass, and keep a record that survives the loss of your context (compaction, a new session).

## Setup

1. Work on the plan's branch, never on `main` (`core/git.md`). Create it if it does not exist yet; say so.
2. Read the plan once, then the spec it names: the spec is the authority, the plan argues from it. A plan with no reachable spec gets a line in *Progress*: rulings made without one are provisional.
3. Read *Progress*: ticked tasks are done, even if you do not remember them. Trust the plan and `git log` over your recollection. Resume at the first unticked task.
4. Before Task 1, check the interfaces between tasks: for each task that consumes what an earlier one produces, do the names and types match? Settle the mismatches as rulings.
5. Load `ai-rules-test-driven-development` before Task 1: it governs every step.

## Each task

1. **Re-read the task** in the plan, even if you remember it: memory keeps a summary, the plan keeps the exact values.
2. **Check the tier**: if the running model or effort does not match it, say it in one line (`ai-rules-writing-plans`), then continue unless the user stops you.
3. **Work the steps in order.** Every step that runs a command has an expected result: run it, read the output, compare.
   - Matches: next step.
   - The code is wrong: `ai-rules-systematic-debugging`; never patch the symptom to match the expectation.
   - The plan is wrong (contradicts the spec, an interface does not match, a command cannot work): if the smallest fix does not change behavior, scope or structure, apply it and record `Ruling: <finding> — <decision and why> — <cost if wrong>` in *Progress*. Otherwise stop and ask (`core/principles.md`: propose options before deciding).
4. **Done** only with evidence from this session (`ai-rules-verification-before-completion`): every test the task names ran and passed, every expected result was compared, every deviation has a ruling. Then tick the task in *Progress*, in the same edit as the last change of the task.

Keep the context lean: send long test output to a file and read its tail.

## Commit points

At each commit point of the plan: run the whole test suite and the project's checks, self-review the diff (`ai-rules-reviewing-changes`), update the docs, write `.private/COMMIT_MESSAGE`, give the command block, and **stop** until the user says to continue (`core/commits.md`). Never commit, push or merge yourself.

Between commit points, do not stop to ask "should I continue?". Stop only for:

- a decision that changes behavior, scope or structure;
- an irreversible or destructive action, or anything security-sensitive;
- an action outside the working tree (push, publish, external service);
- a plan so broken that every path forward is a guess.

## Handoff

When the session grows heavy (long outputs, many tasks behind, a compaction close) or the topic changes, propose a handoff note in `.private/HANDOFF.md`: branch and last commit, tasks done and remaining, rulings, open points, next action, and a **Resume** section with the prompt to paste after `/clear`, the commands that check the state (`git status`, `git log -3`, the test command) and the files to reread (the plan, the spec). Write it when the user agrees.

## Final review

After the last task, review the whole branch against the spec and the plan's review focus with `ai-rules-reviewing-changes`, as a separate pass. Grade each finding by what a user would get if it shipped, not by whether the spec mentions it:

- **Blocking or important**: fix in one pass, each fix test-first (reproduce, watch it fail, fix, run the suite).
- **Minor**: list it under "Deferred" in *Progress*; do not fix it unasked.
- **A finding you decide not to fix** is a ruling.

Then report to the user: what was done, the rulings in order with their cost if wrong, the deferred findings, and that the final review was a self-review by the author. Continue with the last commit point.

## Rationalizations

| Excuse | Reality |
|---|---|
| "I remember what the task says" | You remember a summary. Re-read it |
| "The test will fail anyway, skip watching it" | A test never seen failing proves nothing |
| "The plan is wrong, I'll just do the right thing" | Do it and record the ruling, or ask if it changes behavior |
| "I'll update Progress after a few tasks" | Compaction does not wait. Tick it with the task |
| "It's a small change, I'll commit it myself" | Never. Commit message, command block, stop |
| "I'll fix the minor findings while I'm here" | The user decides. List them |
