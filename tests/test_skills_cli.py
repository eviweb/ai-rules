from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from tests.test_skills import write_skill

RUNNER = CliRunner()


def agents_toml(install_root: Path, with_skills: bool) -> str:
    skills = (
        '\n  [[agents.claude.skill_dirs]]\n  source = "skills"\n  target = "skills"\n'
        if with_skills
        else ""
    )
    return f"""
[agents.claude]
name             = "Claude Code"
entry_point      = "agents/claude/CLAUDE.md"
install_dir      = "{install_root}/claude"
supports_imports = true
{skills}
[agents.codex]
name             = "Codex"
entry_point      = "agents/codex/AGENTS.md"
install_dir      = "{install_root}/codex"
"""


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (tmp_path / "install").mkdir()
    (root / "agents.toml").write_text(agents_toml(tmp_path / "install", True))
    return root


def invoke(args: list[str], repo: Path) -> object:
    return RUNNER.invoke(app, ["--no-log", *args], env={"AI_RULES_HOME": str(repo)})


def test_skills_list_shows_name_size_and_description(repo: Path) -> None:
    write_skill(repo / "skills", "ai-rules-demo")

    result = invoke(["skills", "list"], repo)

    assert result.exit_code == 0
    assert "ai-rules-demo" in result.output
    assert "Use when reviewing" in result.output


def test_skills_list_marks_invalid_skill(repo: Path) -> None:
    write_skill(repo / "skills", "ai-rules-bad", frontmatter="name: ai-rules-bad\n")

    result = invoke(["skills", "list"], repo)

    assert result.exit_code == 0
    assert "ai-rules-bad" in result.output
    assert "invalid" in result.output


def test_skills_list_without_skills_says_so(repo: Path) -> None:
    result = invoke(["skills", "list"], repo)

    assert result.exit_code == 0
    assert "No skills" in result.output


def test_skills_verify_passes_on_valid_skills(repo: Path) -> None:
    write_skill(repo / "skills", "ai-rules-demo")

    result = invoke(["skills", "verify"], repo)

    assert result.exit_code == 0
    assert "1 skill" in result.output


def test_skills_verify_fails_and_lists_problems(repo: Path) -> None:
    write_skill(repo / "skills", "ai-rules-bad", frontmatter="name: ai-rules-bad\n")

    result = invoke(["skills", "verify"], repo)

    assert result.exit_code == 1
    assert "ai-rules-bad" in result.output
    assert "description" in result.output


def test_skills_verify_without_skills_passes(repo: Path) -> None:
    result = invoke(["skills", "verify"], repo)

    assert result.exit_code == 0
    assert "0 skills" in result.output


def test_skills_status_reports_deployment_per_agent(repo: Path) -> None:
    write_skill(repo / "skills", "ai-rules-demo")

    before = invoke(["skills", "status"], repo)
    invoke(["install", "claude"], repo)
    after = invoke(["skills", "status"], repo)

    assert "not installed" in before.output
    assert "claude" in before.output
    assert "codex" not in before.output
    assert after.exit_code == 0
    assert "ok" in after.output


def test_skills_status_without_skill_directory_says_so(
    repo: Path, tmp_path: Path
) -> None:
    (repo / "agents.toml").write_text(agents_toml(tmp_path / "install", False))

    result = invoke(["skills", "status"], repo)

    assert result.exit_code == 0
    assert "No agent deploys skills" in result.output
