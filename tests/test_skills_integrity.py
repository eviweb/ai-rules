from __future__ import annotations

from pathlib import Path

from ai_rules.skills import verify_skills

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repository_skills_respect_the_format_rules() -> None:
    problems = verify_skills(REPO_ROOT / "skills", REPO_ROOT)

    assert problems == {}
