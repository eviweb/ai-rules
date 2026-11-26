from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.agent import SkillDir, load_agents

REPO_ROOT = Path(__file__).resolve().parent.parent

# `docs.md` stays a scoped rule while `ai-rules-starting-a-project` carries the
# same wording: the two copies must not drift apart.
DUPLICATED_RULES = {"ai-rules-starting-a-project": ["docs.md"]}

# Rules whose skill is the single source: they must not also live in rules/.
SKILL_OWNED_RULES = ["editor.md", "quality.md", "review.md", "pr.md", "issues.md", "release.md"]

SKILLS = [
    "ai-rules-starting-a-project",
    "ai-rules-quality-dimensions",
    "ai-rules-reviewing-changes",
    "ai-rules-pull-requests-and-issues",
]


def _skill_text(name: str) -> str:
    folder = REPO_ROOT / "skills" / name
    parts = [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]
    return "\n".join(path.read_text() for path in parts if path.exists())


@pytest.mark.parametrize(
    "skill, rule",
    [(skill, rule) for skill, rules in DUPLICATED_RULES.items() for rule in rules],
)
def test_skill_carries_the_scoped_rule_text_unchanged(skill: str, rule: str) -> None:
    from ai_rules.generator import split_frontmatter

    rule_text = split_frontmatter((REPO_ROOT / "rules" / rule).read_text())[1].strip()

    assert rule_text in _skill_text(skill)


def test_every_skill_exists() -> None:
    missing = [
        name
        for name in SKILLS
        if not (REPO_ROOT / "skills" / name / "SKILL.md").is_file()
    ]

    assert missing == []


def test_claude_deploys_the_skills_directory() -> None:
    claude = load_agents(REPO_ROOT / "agents.toml")["claude"]

    assert SkillDir(source="skills", target="skills") in claude.skill_dirs


def test_codex_deploys_the_skills_to_its_user_skills_directory() -> None:
    codex = load_agents(REPO_ROOT / "agents.toml")["codex"]

    assert SkillDir(source="skills", target="~/.agents/skills") in codex.skill_dirs


@pytest.mark.parametrize("rule", SKILL_OWNED_RULES)
def test_skill_owned_rule_is_not_also_a_rule_file(rule: str) -> None:
    assert not (REPO_ROOT / "rules" / rule).exists()
    assert not (REPO_ROOT / "core" / rule).exists()


def test_no_skill_duplicates_core_content() -> None:
    skill_text = "\n".join(_skill_text(name) for name in SKILLS)
    duplicated = [
        f.name
        for f in sorted((REPO_ROOT / "core").glob("*.md"))
        if f.read_text().strip() in skill_text
    ]

    assert duplicated == []
