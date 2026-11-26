from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "skills"
PLANNING_SKILLS = ["ai-rules-brainstorming", "ai-rules-writing-plans", "ai-rules-executing-plans"]


def _skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text()


@pytest.mark.parametrize("name", PLANNING_SKILLS)
def test_planning_skill_is_derived_from_the_pinned_upstream(name: str) -> None:
    upstream = name.removeprefix("ai-rules-")

    assert f'derived-from: "superpowers/{upstream} @ 22f0b46"' in _skill(name)


def test_brainstorming_gates_building_on_an_approved_design() -> None:
    text = _skill("ai-rules-brainstorming")

    assert "Nothing is built until the user approves the design" in text
    assert "`ai-rules-writing-plans`" in text
    assert "`ai-rules-architecture-proposal`" in text


def test_brainstorming_ranks_candidates_by_value_and_complexity() -> None:
    text = _skill("ai-rules-brainstorming")

    assert "## Rank the candidates" in text
    assert "value" in text and "complexity" in text
    assert "`TODO.md`" in text


def test_brainstorming_writes_specs_and_designs_with_the_writing_skill() -> None:
    text = _skill("ai-rules-brainstorming")

    assert "`docs/specs/`" in text and "`docs/design/`" in text
    assert "`ai-rules-writing-documents`" in text


def test_brainstorming_time_boxes_spikes() -> None:
    assert "time box" in _skill("ai-rules-brainstorming")


def test_writing_plans_inspects_the_repository_first() -> None:
    text = _skill("ai-rules-writing-plans")

    assert text.index("**Inspect the repository**") < text.index("## Tasks")


def test_writing_plans_tasks_carry_ready_done_tier_and_refactor() -> None:
    text = _skill("ai-rules-writing-plans")

    for field in ("**Ready**", "**Done**", "**Tier**", "refactor"):
        assert field in text


def test_writing_plans_saves_plans_in_the_private_directory() -> None:
    assert "`.private/plans/YYYY-MM-DD-<topic>.md`" in _skill("ai-rules-writing-plans")


def test_writing_plans_defaults_to_one_commit_point_per_branch_and_never_commits() -> None:
    text = _skill("ai-rules-writing-plans")

    assert "one commit per branch" in text
    assert "The agent never commits" in text


def test_writing_plans_maps_tiers_without_looking_models_up() -> None:
    text = _skill("ai-rules-writing-plans")

    assert "`~/.config/ai-rules/model-tiers.md`" in text
    assert "checked: YYYY-MM-DD" in text
    assert "`/model`" in text
    assert "Do not look them up yourself" in text
    assert "never switch models on your own" in text


def test_executing_plans_stops_at_each_commit_point() -> None:
    text = _skill("ai-rules-executing-plans")

    assert "`.private/COMMIT_MESSAGE`" in text
    assert "**stop**" in text
    assert "Never commit, push or merge yourself" in text


def test_executing_plans_asks_before_rulings_that_change_behavior() -> None:
    text = _skill("ai-rules-executing-plans")

    assert "Ruling:" in text
    assert "Otherwise stop and ask" in text


def test_executing_plans_proposes_a_handoff_note_with_resume_instructions() -> None:
    text = _skill("ai-rules-executing-plans")

    assert "`.private/HANDOFF.md`" in text
    assert "**Resume**" in text and "`/clear`" in text


def test_executing_plans_ends_with_a_whole_branch_review() -> None:
    text = _skill("ai-rules-executing-plans")

    assert "## Final review" in text
    assert "`ai-rules-reviewing-changes`" in text
    assert "self-review" in text
