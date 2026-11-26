---
name: ai-rules-finishing-a-branch
description: "Use when the work on a branch is complete and verified, to integrate it: confirm the base, prepare the commit message and the pull request, give the user the full command block (commit, push, PR, checks, merge, cleanup), then help with failing checks and the cleanup."
metadata:
  derived-from: "superpowers/finishing-a-development-branch @ 22f0b46"
  license-of-origin: MIT
---
# Finishing a branch

The agent prepares the integration; the user runs it. Committing, pushing and merging are the user's actions (`core/commits.md`): they hold the signing keys and the decision. The agent's job is to make each of those steps one paste away and correct.

## 1. Verify the tree you are about to integrate

- Run the whole test suite and the project's checks now, on this tree (`ai-rules-verification-before-completion`). A green run earlier in the session proves nothing about the current tree. If anything fails, report it and stop.
- Review the change (`ai-rules-reviewing-changes`): review package, checklist, docs (`README.md`, `CHANGELOG.md`, `TODO.md`) updated in the same commit.

## 2. Confirm the base and the remote

- The base is the branch this work started from, usually `main`. If it is not certain, ask: merging into the wrong base is expensive to undo.
- Read the remote names with `git remote -v`; use the one that points to the forge (it may be `github`, `origin`, `upstream`…). Ask if several qualify.
- Check whether the base moved (`git fetch`, then `git log --oneline HEAD..<remote>/<base>`). If it did and the branch is not shared, propose `git rebase <base>` (`core/git.md`).

## 3. Offer the ways to finish

```
The work on <branch> is ready. How do you want to finish it?

1. Pull request toward <base> (required in the strict profile)
2. Merge locally into <base> (light profile, trivial docs or chore changes only)
3. Keep the branch as it is for now
```

Wait for the answer. Throwing the work away is not an option on this list: it happens only when the user asks for it in so many words (see *Discarding*).

## 4. Prepare what the chosen way needs

- **Commit message** in `.private/COMMIT_MESSAGE` (`core/commits.md`), covering every changed file.
- **Pull request** title and body following the project's template (`ai-rules-pull-requests-and-issues`); a title with `!` goes in single quotes in shell commands.
- **The command block**, adapted to this branch, files added one by one (never `git add -A` or `.`):

```bash
git add <file> …
git commit -s -F .private/COMMIT_MESSAGE
git push -u <remote> <branch>
gh pr create --base <base> --title "<title>" --body "$(cat <<'EOF'
<body following the PR template>
EOF
)"
sleep 15                    # let the checks register before watching them
gh pr checks --watch
gh pr merge --merge --subject "Merge pull request from <owner>/<branch>" --body "<title>"
git checkout <base>
git pull
git branch -d <branch>
git push <remote> --delete <branch>
```

Merge commit (`--merge`) keeps the commit signatures (`core/git.md`). On another forge, use its CLI the same way (for example `tea pulls create` on Forgejo). For option 2, the block is `git checkout <base>`, `git merge --no-ff <branch>`, the test suite on the merged result, then `git branch -d <branch>`; if the tests fail on the merged result, stop: nothing is pushed yet.

## 5. After the user runs it

- **Checks fail**: read the failing job (`gh pr checks`, `gh run view --log-failed`), find the cause (`ai-rules-systematic-debugging`), fix it test-first, and give the next commit and push commands. A rejected push means the remote moved: investigate, never force-push unless the user asks for it on a personal branch.
- **Review comments**: `ai-rules-receiving-code-review`.
- **Merged**: confirm that the base is up to date and the branch is gone locally and on the remote (`git branch -d` fails if the PR was merged another way: check with `gh pr view <number> --json state -q .state`, then use `-D` with the user's agreement). Then propose cleaning what this work left in `.private/` (drafts, review packages, the plan once its progress is recorded): list the files, delete only on the user's go.

## Discarding

Only on an explicit request. List what would be lost (branch, commits not merged anywhere, uncommitted files), ask the user to confirm by typing `discard`, then give the commands (`git checkout <base>`, `git branch -D <branch>`, `git push <remote> --delete <branch>` if it was pushed). Never `--force` anything on your own.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The tests passed earlier" | Run them on the tree being integrated |
| "They obviously want it merged" | The user chooses. Offer the options and wait |
| "It's just a push" | Pushing publishes. The user runs it |
| "The base is obviously main" | Confirm it when there is any doubt |
| "The push was rejected, force-push will fix it" | The remote moved. Investigate first |
| "I'll clean `.private/` while I'm at it" | List the files and ask |
