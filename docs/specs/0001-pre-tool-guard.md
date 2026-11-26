# 0001 — Pre-tool guard for agent shell commands

Status: approved 2026-11-26. Roadmap phase 5, part A (0.10.0). Claude Code only.

## Problem and goal

The permission rules deployed in `~/.claude/settings.json` deny destructive commands (`rm -r`, `git push --force`, `git reset --hard`, `git clean`, `git checkout --`, `git branch -D`) and ask before `git commit`, `git push` and `rm`. Claude Code applies them to every subcommand of a compound command and strips wrappers such as `xargs` and `timeout`, but, as its documentation states, a rule "doesn't match the same program invoked in a different form": `bash -c 'rm -rf x'`, `/bin/rm -rf x`, `git -C ../x push --force` or `git push origin +main` pass. Nothing checks that a commit made by the agent uses the message the user reviewed.

Goal: a `PreToolUse` hook that closes these gaps for the commands the agent runs, without prompting for harmless commands. It is a seatbelt against mistakes, not a sandbox against a determined adversary.

## Users and scenarios

- The user works with Claude Code; the agent runs shell commands through the `Bash` tool. The user commits, pushes and merges in their own terminal, which the hook never sees.
- The agent writes a destructive command in a form the rules miss: the hook denies it and tells the agent why, or asks the user.
- The user explicitly asks the agent to commit: the agent may run only `git commit -s -F .private/COMMIT_MESSAGE`, and the user still confirms it.

## Requirements

Inspection

- **R1** When the `Bash` tool is about to run, the guard shall read the hook input from stdin and inspect `tool_input.command`.
- **R2** The guard shall split the command into simple commands at `&&`, `||`, `;`, `|`, `&` and newlines, outside quotes, and inspect each one. The body of a here-document (`<<WORD`, `<<'WORD'`, `<<"WORD"`, `<<-WORD`, up to the line holding only `WORD`) is not split into commands: it belongs to the command that opens it and is only scanned by R9. Otherwise a script that merely contains the text `git commit -m` or `rm -rf` would be denied.
- **R3** The guard shall normalize each simple command before matching: drop leading `NAME=value` assignments and the wrappers `env`, `command`, `exec`, `nohup`, `nice`, `timeout <duration>`, `xargs`, `sudo`, `doas` (with their options); reduce a program given by path (`/bin/rm`, `./rm`) to its name.
- **R4** When a simple command runs `bash`, `sh`, `zsh` or `dash` with `-c <string>`, or `eval <words>`, the guard shall inspect the string as a command, up to three levels deep; deeper nesting is asked (R12).

Decisions

- **R5** When a simple command is `rm` with a recursive option (`-r`, `-R`, `--recursive`, alone or combined with others such as `-rf` or `-fR`), the guard shall deny it.
- **R5b** When a simple command runs through `sudo` or `doas`, at any level, the guard shall deny it: the `Bash(sudo *)` rule does not see inside `bash -c`, and no rule covers `doas`.
- **R6** When a simple command is `find` with `-delete`, or with `-exec`/`-execdir` running `rm`, or is `shred`, the guard shall ask.
- **R7** When a simple command is `git`, the guard shall skip its global options (`-C <path>`, `-c <key=value>`, `--git-dir=…`, `--work-tree=…`, `--no-pager`, `-P`) and then:
  - deny `push` with `--force`, `-f`, a combined short option containing `f`, or a refspec starting with `+`;
  - ask for `push --force-with-lease` (with or without a value);
  - deny `reset --hard`, `clean` with any option, `checkout --`, `branch -D` and `branch --delete --force`.
- **R8** When a simple command is `git commit`, the guard shall allow it to reach the permission prompt only if its options are exactly `-s` or `--signoff` and `-F`, `--file <path>` or `--file=<path>`, in any order, where the path resolves to `.private/COMMIT_MESSAGE` at the top of the repository and that file exists and is not empty, and no git global option `-c` sets `core.hooksPath`, `commit.gpgSign` or a `user.*` key (which would bypass the commit hooks, the signature or the identity, like `--no-verify`). Any other form shall be denied, naming the expected command.
- **R9** When a simple command runs `python`, `python3`, `perl`, `ruby` or `node` with inline code (`-c`, `-e`, or a script read from stdin such as `python3 - <<'EOF'`), and that code contains a deletion or process primitive (`rmtree`, `unlink`, `remove`, `rmdir`, `os.system`, `subprocess`, `rm -`), the guard shall ask. Inline code without such a primitive is not flagged.
- **R10** If no requirement matches, the guard shall make no decision, so that the permission rules apply as before.

Output and failure

- **R11** The guard shall report a deny or an ask as `hookSpecificOutput` with `permissionDecision` and a `permissionDecisionReason` in English that names the matched form and the expected alternative; when several simple commands match, the most restrictive decision wins (deny over ask).
- **R12** If the input cannot be read or parsed, or a quote is unbalanced, then the guard shall ask, with a reason saying the command could not be analysed.
- **R13** If the guard itself fails (an exception), then it shall exit with a non-zero code other than 2 and a message on stderr, so that Claude Code shows a hook error and the permission rules still apply.

Deployment

- **R14** `ai-rules install` and `update` shall link the guard into `~/.claude/hooks/` and register it under `hooks.PreToolUse` with matcher `Bash` through the settings merge, without touching the user's own hooks; `remove` shall unregister and unlink it.
- **R15** `ai-rules status` shall report whether the guard is linked, registered, and whether `python3` is found.

## Acceptance criteria

```gherkin
Given the guard is registered
When the agent runs "bash -c 'rm -rf build'"
Then the call is denied and the reason names the recursive rm

When the agent runs "/bin/rm -fr /tmp/x"
Then the call is denied

When the agent runs "git -C ../other push --force origin main"
Then the call is denied

When the agent runs "git push origin +main"
Then the call is denied

When the agent runs "git push --force-with-lease"
Then the user is asked

When the agent runs "find . -name '*.pyc' -delete"
Then the user is asked

When the agent runs "git commit -s -F .private/COMMIT_MESSAGE" and the file is not empty
Then the guard makes no decision and the existing ask rule prompts the user

When the agent runs "git commit -m 'fix'" or "git commit --amend -s -F .private/COMMIT_MESSAGE" or "git commit --no-verify -s -F .private/COMMIT_MESSAGE"
Then the call is denied and the reason gives the expected command

When the agent runs "bash -c 'sudo rm -rf /x'" or "doas rm -rf /x"
Then the call is denied

When the agent runs "git -c core.hooksPath=/dev/null commit -s -F .private/COMMIT_MESSAGE"
Then the call is denied and the reason gives the expected command

When the agent runs "python3 -c 'import shutil; shutil.rmtree(\"x\")'"
Then the user is asked

When the agent runs "python3 -c 'print(1)'", "git -C . status", "bash -c 'ls'" or "rm file.txt"
Then the guard makes no decision

When the agent runs "python3 - <<'EOF'" with a body that only edits a text file containing the words "git commit -m"
Then the guard makes no decision

When the input is not valid JSON
Then the user is asked with a reason saying the command could not be analysed
```

Each scenario becomes a test; the test corpus holds every example of this spec and the variants of `rm` options, quoting and nesting.

## Quality requirements

- **Performance**: ≤ 50 ms per invocation at the 95th percentile on the test corpus, measured by a test (Python startup measured at 22 ms on the development machine).
- **Security**: fail-safe on unreadable input (ask), fail-visible on a crash (hook error shown, rules still apply); the guard never returns `allow`, so it can only make the existing rules stricter.
- **Testability**: a pure function `decide(command, repo_root) -> Decision` holds the logic; the hook script only reads stdin and prints the result.
- **Dependencies**: Python standard library only (`json`, `shlex`, `os`); runs with `python3 -I -S`.

## Non-goals

- Codex and Gemini hooks (phase 6), the session-start bootstrap (phase 5, part B, after usage data).
- A complete POSIX shell parser: here-documents are scanned as text (R9), not parsed; command substitutions are inspected only where Claude Code's own splitting already covers them.
- Scripts in files (`./cleanup.sh`, `make clean`): their content is not read.
- Commands typed by the user in their own terminal.

## Decisions taken

- R5b and the `-c` part of R8 were added on 2026-11-26 after the final review of the implementation found `bash -c 'sudo rm -rf …'`, `doas` and `git -c core.hooksPath=… commit` passing.
- R7 denies `git checkout --` in every form, including `git checkout -- <file>`, like the existing rule: it discards uncommitted work.
- R9 is a heuristic on keywords: it will ask for some harmless code (a variable named `remove`) and miss obfuscated code. Accepted by the user on 2026-11-26 as a deliberate trade-off between friction and protection; to revisit after use.
