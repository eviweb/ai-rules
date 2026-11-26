"""Claude Code PreToolUse hook: deny or ask for risky agent shell commands.

Run as ``python3 -I -S <this file>``. Reads the hook input JSON on stdin and
prints a decision only when the guard makes one (``deny`` or ``ask``); no
output means the permission rules decide as usual. On an internal error it
exits 1 with a message on stderr: Claude Code shows a hook error and the
permission rules still apply. Spec: ``docs/specs/0001-pre-tool-guard.md``.

The guard logic lives in ``src/ai_rules/guard.py`` and is loaded by path, so
that the hook needs neither the installed package nor ``PYTHONPATH``.
"""

from __future__ import annotations

import json
import os
import sys

# Imported by path from the repository the hook is linked from; the hook runs
# before every agent shell command, so it avoids importlib.util and pathlib.
GUARD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src", "ai_rules")
UNREADABLE = "the command could not be analysed (invalid hook input); ask the user to confirm it"


def _load_guard():
    sys.path.insert(0, GUARD_DIR)
    import guard

    return guard


def _emit(action: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": action,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        if payload.get("tool_name") != "Bash":
            return 0
        command = payload["tool_input"]["command"]
        if not isinstance(command, str):
            raise TypeError("tool_input.command is not a string")
        cwd = payload.get("cwd") or os.getcwd()
    except (ValueError, AttributeError, KeyError, TypeError):
        _emit("ask", UNREADABLE)
        return 0

    try:
        decision = _load_guard().decide(command, cwd)
    except Exception as error:  # noqa: BLE001 — any guard failure must stay visible, never silent
        print(f"ai-rules pre-tool-guard failed: {error!r}", file=sys.stderr)
        return 1
    if decision.action is not None:
        _emit(decision.action, decision.reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
