from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "ai-rules-refactoring-and-design"
REFERENCES = SKILL / "references"
STACKS = REFERENCES / "stacks"
MAX_STACK_BYTES = 2 * 1024

GOF_PATTERNS = [
    "Abstract Factory", "Builder", "Factory Method", "Prototype", "Singleton",
    "Adapter", "Bridge", "Composite", "Decorator", "Facade", "Flyweight", "Proxy",
    "Chain of Responsibility", "Command", "Interpreter", "Iterator", "Mediator",
    "Memento", "Observer", "State", "Strategy", "Template Method", "Visitor",
]
EXTRA_PATTERNS = [
    "Bridge", "Flyweight", "Interpreter", "Iterator", "Memento", "Mediator",
    "Prototype", "Visitor",
]


def _stack_files_named_in_skill() -> set[str]:
    text = (SKILL / "SKILL.md").read_text()
    return set(re.findall(r"references/stacks/([a-z-]+)\.md", text))


def test_every_stack_file_is_listed_in_the_skill_and_the_reverse() -> None:
    on_disk = {p.stem for p in STACKS.glob("*.md")}

    assert on_disk == _stack_files_named_in_skill()


@pytest.mark.parametrize("stack_file", sorted(STACKS.glob("*.md")), ids=lambda p: p.stem)
def test_stack_file_stays_within_its_size_budget(stack_file: Path) -> None:
    assert stack_file.stat().st_size <= MAX_STACK_BYTES


def test_stack_files_cover_the_supported_languages() -> None:
    names = {p.stem for p in STACKS.glob("*.md")}

    assert {"shell", "python", "js-ts", "go", "rust", "php", "common"} <= names


@pytest.mark.parametrize("pattern", GOF_PATTERNS)
def test_pattern_index_names_every_gof_pattern(pattern: str) -> None:
    assert pattern in (REFERENCES / "patterns.md").read_text()


@pytest.mark.parametrize("pattern", EXTRA_PATTERNS)
def test_rarer_patterns_are_detailed_in_the_extra_file(pattern: str) -> None:
    assert f"**{pattern}**" in (REFERENCES / "patterns-extra.md").read_text()


def test_skill_reports_structural_problems_instead_of_fixing_them() -> None:
    text = (SKILL / "SKILL.md").read_text()

    for required in ("refactoring proposal", "Options", "do nothing", "wait for the user"):
        assert required in text


def test_skill_states_the_arbiter_order_and_chestertons_fence() -> None:
    text = (SKILL / "SKILL.md").read_text()

    assert text.index("**Correct**") < text.index("**Simple**") < text.index("**Readable**")
    assert text.index("**Readable**") < text.index("**DRY**")
    assert "Chesterton" in text


def test_skill_has_no_boy_scout_rule_and_reports_what_it_notices() -> None:
    text = (SKILL / "SKILL.md").read_text()

    assert "boy-scout" not in text.lower()
    assert "Notice and report" in text


def test_skill_defers_to_the_project_linter_for_thresholds() -> None:
    smells = (REFERENCES / "smells.md").read_text()

    assert "linter configuration" in smells
    assert "cognitive complexity" in smells


def test_skill_routes_deferred_debt_by_project_profile() -> None:
    text = (SKILL / "SKILL.md").read_text()

    assert "TODO.md" in text and "issue" in text and "profile" in text


def test_smells_cover_test_code() -> None:
    assert "Test smells" in (REFERENCES / "smells.md").read_text()


def test_principles_cover_the_added_working_principles() -> None:
    principles = (REFERENCES / "principles.md").read_text()

    for required in (
        "Convention over configuration",
        "Four rules of simple design",
        "Spike",
        "Definition of ready",
        "Definition of done",
        "Modern Agile",
        "Design thinking",
    ):
        assert required in principles


def test_refactorings_cover_schema_changes_and_feature_flags() -> None:
    text = (REFERENCES / "refactorings.md").read_text()

    assert "database schema" in text.lower()
    assert "feature flag" in text.lower()


def test_claude_entry_point_gives_the_working_chain() -> None:
    entry_point = (REPO_ROOT / "agents" / "claude" / "CLAUDE.md").read_text()

    assert "brainstorming" in entry_point and "verification" in entry_point.lower()
    assert "Typical flow" in entry_point
