---
name: ai-rules-receiving-code-review
description: "Use when receiving review feedback (from the user, a pull request comment, another agent or a review tool), before changing anything: understand every item, check it against the code, answer with facts or reasoned pushback, then fix one item at a time, test-first."
metadata:
  derived-from: "superpowers/receiving-code-review @ 22f0b46"
  license-of-origin: MIT
---
# Receiving code review

Review feedback is a claim to check, not an order to execute or a compliment to return. Verify before implementing, ask before assuming, and prefer technical correctness to social comfort.

## The response

1. **Read** all the feedback before acting on any item.
2. **Understand**: restate each item as a technical requirement. If **any** item is unclear, ask about it before implementing **anything**: items are often related, and a partial understanding gives a wrong fix ("I understand 1, 2, 3 and 6; what do you mean by 4 and 5?").
3. **Verify** against the code as it is: read the code, the tests, the history (why is it like this?), the targets (versions, platforms).
4. **Evaluate**: is it right for this project, its constraints and the user's earlier decisions?
5. **Answer**: state the fix, or push back with evidence.
6. **Fix** one item at a time, test-first, and run the suite after each.

No performative agreement ("You're absolutely right!", "Great catch!", thanks for the feedback). State what you checked and what you changed; the fix shows that the feedback was heard.

## By source

- **The user**: trusted on intent. Understand, then act; still ask when the scope is unclear, and still say so when a request would break something.
- **External reviewers** (pull request comments, another agent, a review bot, a linter): check before acting. Is it correct for this code base? Does it break existing behavior or compatibility? Is there a reason for the current code? Does the reviewer have the full context? If it contradicts a decision the user made, stop and ask the user.
- **When you cannot verify** a claim: say so and what you would need ("I cannot check this without the production logs; investigate, ask, or proceed?").

## Push back when

- the suggestion breaks existing behavior or a supported platform;
- the reviewer lacks context (a compatibility constraint, an earlier decision);
- it adds something nothing uses: check for real callers first (YAGNI; "nothing calls this endpoint: remove it rather than complete it?");
- it is wrong for this stack or conflicts with the architecture the user chose.

Push back with facts: the test that proves the behavior, the line that needs it, the decision record. If the disagreement is about design or scope, the user decides. If you pushed back and were wrong, say so in one line ("Checked: you are right, `x` does `y`; fixing.") and move on.

## Order of the fixes

1. Clarify everything unclear first.
2. Blocking issues (breakage, security), then simple fixes, then complex ones (logic, refactoring).
3. Each fix test-first when it changes behavior (`ai-rules-test-driven-development`), the whole suite after each, the review checklist at the end (`ai-rules-reviewing-changes`).
4. Then propose the commit as usual (`core/commits.md`); never commit or push on your own.

## Replying on the platform

Replies on a pull request are public. Draft them in the conversation, short and factual (what changed, where, or why not), and post only when the user agrees. Reply in the thread of the inline comment (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level comment. Resolving threads is the user's call.
