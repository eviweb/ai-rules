from __future__ import annotations

from pathlib import Path

from ai_rules.skills import verify_skills

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repository_skills_respect_the_format_rules() -> None:
    problems = verify_skills(REPO_ROOT / "skills", REPO_ROOT)

    assert problems == {}


def test_claude_entry_point_indexes_every_skill() -> None:
    entry_point = (REPO_ROOT / "agents" / "claude" / "CLAUDE.md").read_text()
    skills = sorted(p.name for p in (REPO_ROOT / "skills").iterdir() if p.is_dir())

    missing = [name for name in skills if name not in entry_point]

    assert missing == []
