# Git Commits

## Format
- Follow Conventional Commits: `type(scope): message`
- Never include emojis in commit messages — the global `commit-msg` hook adds them automatically via `insert-icon`
- Always use `git commit -s` to append a `Signed-off-by` trailer (DCO compliance + GPG signing)
- **Prefer detailed commit messages** — whenever a commit touches multiple files or introduces non-obvious changes, add a body listing the key changes. A one-liner is acceptable only for genuinely trivial commits (e.g. typo fix, single-line change). When in doubt, add detail:

  ```
  type(scope): short summary

  - Change A: why it was needed
  - Change B: what it replaces or fixes
  - Change C: any non-obvious consequence
  ```

## Hook behavior
- The global `commit-msg` hook runs `cog verify` then `insert-icon`
- Check that `LEGACY_COMMIT_MESSAGE` is `0` before committing to ensure the hook runs
- Set `git config hook.legacyCommitMessage true` in two cases (bypasses the hook entirely — no icon added):
  1. The message intentionally does NOT follow Conventional Commits
  2. The existing commit history uses the old format (plain message without `type(scope):`) — use legacy mode to maintain consistency within that repository

## Claude Code commit workflow
- **Never commit autonomously.** Commits must be explicitly requested by the user AND confirmed before execution.
- After every set of modifications, always propose a commit message covering **all modified files** — code, tests, and documentation included.
- Wait for the user's explicit go-ahead before running any `git commit` command.
