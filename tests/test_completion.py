from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

AGENTS_TOML = """
[agents.claude]
name = "Claude Code"
entry_point = "agents/claude/CLAUDE.md"
install_dir = "~/.claude"
supports_imports = true

[agents.codex]
name = "Codex"
entry_point = "agents/codex/AGENTS.md"
install_dir = "~/.codex"
"""


@pytest.fixture()
def home(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "agents.toml").write_text(AGENTS_TOML)
    return root


ENTRY = "from ai_rules.cli import app; app(prog_name='ai-rules')"


def complete(words: str, shell: str = "bash", *, env_home: Path | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Ask the CLI for completions the way the shell completion script does."""
    env = {k: v for k, v in os.environ.items() if k != "AI_RULES_HOME"}
    if env_home is not None:
        env["AI_RULES_HOME"] = str(env_home)
    env["_AI_RULES_COMPLETE"] = f"complete_{shell}"
    if shell == "bash":
        typed = words.split()
        env["COMP_WORDS"] = words
        env["COMP_CWORD"] = str(len(typed) if words.endswith(" ") else len(typed) - 1)
    else:
        env["_TYPER_COMPLETE_ARGS"] = words
    return subprocess.run(
        [sys.executable, "-c", ENTRY],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=cwd,
    )


@pytest.mark.parametrize("command", ["install", "remove", "update", "status", "generate", "verify"])
def test_agent_keys_are_completed_for_each_command(home: Path, command: str) -> None:
    result = complete(f"ai-rules {command} ", env_home=home)

    assert result.returncode == 0
    assert set(result.stdout.split()) >= {"claude", "codex"}


def test_agent_keys_are_completed_for_skills_status(home: Path) -> None:
    result = complete("ai-rules skills status ", env_home=home)

    assert set(result.stdout.split()) >= {"claude", "codex"}


def test_agent_keys_are_filtered_by_what_was_typed(home: Path) -> None:
    result = complete("ai-rules install c", env_home=home)

    assert set(result.stdout.split()) == {"claude", "codex"}
    narrowed = complete("ai-rules install cl", env_home=home)
    assert narrowed.stdout.split() == ["claude"]


def test_zsh_completion_carries_the_display_name_as_help(home: Path) -> None:
    result = complete("ai-rules install cl", shell="zsh", env_home=home)

    assert "claude" in result.stdout
    assert "Claude Code" in result.stdout


def test_completion_finds_the_register_from_the_working_directory(home: Path) -> None:
    result = complete("ai-rules install cl", cwd=home)

    assert result.stdout.split() == ["claude"]


def test_completion_is_silent_when_no_register_can_be_found(tmp_path: Path) -> None:
    empty = tmp_path / "elsewhere"
    empty.mkdir()

    result = complete("ai-rules install ", cwd=empty)

    assert result.returncode == 0
    assert result.stdout.strip() == ""
    assert result.stderr.strip() == ""


def test_completion_is_silent_when_the_register_is_malformed(tmp_path: Path) -> None:
    broken = tmp_path / "repo"
    broken.mkdir()
    (broken / "agents.toml").write_text("this is [not valid toml")

    result = complete("ai-rules install ", env_home=broken)

    assert result.returncode == 0
    assert result.stderr.strip() == ""


def test_log_dir_paths_are_completed_by_the_shell(tmp_path: Path) -> None:
    """Typer leaves path completion to the shell (files and directories): the CLI proposes nothing itself."""
    (tmp_path / "logs").mkdir()

    result = complete(f"ai-rules --log-dir {tmp_path}/", shell="zsh", cwd=tmp_path)

    assert result.returncode == 0
    assert result.stdout.strip() == "_files"
