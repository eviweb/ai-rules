from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.agent import SkillDir, load_agents

REPO_ROOT = Path(__file__).resolve().parent.parent

# Transition skills (0.7.0): the wording of these rules is carried over
# unchanged. While a rule is still loaded at launch, its text must stay
# identical in the skill, otherwise the two copies drift apart.
TRANSITION_SKILLS = {
    "ai-rules-starting-a-project": ["docs.md", "editor.md"],
    "ai-rules-quality-dimensions": ["quality.md"],
    "ai-rules-reviewing-changes": ["review.md"],
    "ai-rules-pull-requests-and-issues": ["pr.md", "issues.md"],
}


def _skill_text(name: str) -> str:
    folder = REPO_ROOT / "skills" / name
    parts = [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]
    return "\n".join(path.read_text() for path in parts if path.exists())


@pytest.mark.parametrize(
    "skill, rule",
    [(skill, rule) for skill, rules in TRANSITION_SKILLS.items() for rule in rules],
)
def test_transition_skill_carries_its_rule_text_unchanged(skill: str, rule: str) -> None:
    rule_text = (REPO_ROOT / "rules" / rule).read_text().strip()

    assert rule_text in _skill_text(skill)


def test_every_transition_skill_exists() -> None:
    missing = [
        name
        for name in TRANSITION_SKILLS
        if not (REPO_ROOT / "skills" / name / "SKILL.md").is_file()
    ]

    assert missing == []


def test_claude_deploys_the_skills_directory() -> None:
    claude = load_agents(REPO_ROOT / "agents.toml")["claude"]

    assert SkillDir(source="skills", target="skills") in claude.skill_dirs
