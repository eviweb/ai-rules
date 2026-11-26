from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "hooks" / "pre-tool-guard.py"
PYTHON = shutil.which("python3") or "python3"
LATENCY_BUDGET_MS = 50


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "project"
    (path / ".git").mkdir(parents=True)
    (path / ".private").mkdir()
    (path / ".private" / "COMMIT_MESSAGE").write_text("feat: x\n")
    return path


def hook_input(command: str, cwd: Path, tool_name: str = "Bash") -> str:
    return json.dumps(
        {
            "session_id": "test",
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": {"command": command, "description": "test"},
            "cwd": str(cwd),
        }
    )


def run_hook(stdin: str, script: Path = HOOK) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, "-I", "-S", str(script)],
        input=stdin,
        capture_output=True,
        text=True,
        env={"HOME": os.environ.get("HOME", "/tmp")},
        check=False,
    )


def decision_of(result: subprocess.CompletedProcess[str]) -> dict[str, str]:
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    return output


def test_hook_denies_with_the_protocol_json(repo: Path) -> None:
    result = run_hook(hook_input("bash -c 'rm -rf build'", repo))

    assert result.returncode == 0, result.stderr
    output = decision_of(result)
    assert output["permissionDecision"] == "deny"
    assert "rm" in output["permissionDecisionReason"]


def test_hook_asks_with_the_protocol_json(repo: Path) -> None:
    output = decision_of(run_hook(hook_input("git push --force-with-lease", repo)))

    assert output["permissionDecision"] == "ask"


def test_hook_prints_nothing_when_it_makes_no_decision(repo: Path) -> None:
    result = run_hook(hook_input("git status", repo))

    assert result.returncode == 0
    assert result.stdout == ""


def test_hook_ignores_other_tools(repo: Path) -> None:
    result = run_hook(hook_input("rm -rf x", repo, tool_name="Write"))

    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("stdin", ["not json", "[]", json.dumps({"tool_name": "Bash", "tool_input": {}})])
def test_hook_asks_when_the_input_cannot_be_read(stdin: str) -> None:
    output = decision_of(run_hook(stdin))

    assert output["permissionDecision"] == "ask"
    assert "could not be analysed" in output["permissionDecisionReason"]


def test_hook_reports_a_crash_without_deciding(tmp_path: Path, repo: Path) -> None:
    (tmp_path / "hooks").mkdir()
    shutil.copy(HOOK, tmp_path / "hooks" / HOOK.name)
    broken = tmp_path / "src" / "ai_rules"
    broken.mkdir(parents=True)
    (broken / "guard.py").write_text("def decide(command, cwd):\n    raise RuntimeError('boom')\n")

    result = run_hook(hook_input("ls", repo), script=tmp_path / "hooks" / HOOK.name)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "boom" in result.stderr


def test_hook_works_through_a_symlink(tmp_path: Path, repo: Path) -> None:
    link = tmp_path / "ai-rules-pre-tool-guard.py"
    link.symlink_to(HOOK)

    output = decision_of(run_hook(hook_input("rm -rf x", repo), script=link))

    assert output["permissionDecision"] == "deny"


def test_hook_latency_p95_within_budget(repo: Path) -> None:
    commands = [
        "git status",
        "bash -c 'rm -rf build'",
        "git -C x push --force",
        "python3 - <<'EOF'\nprint(1)\nEOF",
        "find . -name x -delete",
    ]
    durations = []
    for index in range(40):
        stdin = hook_input(commands[index % len(commands)], repo)
        start = time.perf_counter()
        run_hook(stdin)
        durations.append((time.perf_counter() - start) * 1000)

    p95 = statistics.quantiles(durations, n=20)[-1]
    print(f"pre-tool-guard latency: p95 {p95:.1f} ms, median {statistics.median(durations):.1f} ms")
    assert p95 <= LATENCY_BUDGET_MS
