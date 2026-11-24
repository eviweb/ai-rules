from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "ai-rules-architecture-proposal"
REFERENCES = SKILL / "references"

STYLES = [
    "Single script or module",
    "Library plus thin CLI",
    "Layered",
    "Modular monolith",
    "Hexagonal (ports and adapters) and clean architecture",
    "Pipes and filters",
    "Plugin or registry (microkernel)",
    "Client-server application (server-rendered or API plus client)",
    "Rich client (GUI or TUI) with separated presentation",
    "Event-driven and message-based",
    "Microservices",
    "Serverless functions",
    "Batch or ETL pipeline",
    "Static site or generated output",
    "Data streaming pipeline",
    "Local-first or offline-first application",
    "Strangler migration (transitional)",
]
STYLE_FIELDS = ["- Shape:", "- Fits:", "- Avoid when:", "- Costs:", "- Reversibility:"]


def _skill() -> str:
    return (SKILL / "SKILL.md").read_text()


def test_skill_requires_three_candidates_including_the_simplest() -> None:
    text = _skill()

    assert "at least three candidates" in text
    assert "simplest thing that could work" in text


def test_skill_compares_recommends_and_waits_before_building() -> None:
    text = _skill()

    for required in ("Compare", "Recommend", "what would change the recommendation", "Wait for the user"):
        assert required in text
    assert text.index("**Compare**") < text.index("**Recommend**") < text.index("**Wait for the user")


def test_skill_records_the_decision_as_an_adr_and_never_scaffolds_or_commits() -> None:
    text = _skill()

    assert "docs/design/adr/" in text
    assert "scaffold" in text and "never commits" in text


def test_skill_forbids_weighted_scores() -> None:
    assert "No weighted scores" in _skill()


@pytest.mark.parametrize("style", STYLES)
def test_catalogue_describes_each_style_with_the_same_fields(style: str) -> None:
    text = (REFERENCES / "architectures.md").read_text()

    assert f"## {style}\n" in text
    section = text.split(f"## {style}\n", 1)[1].split("\n## ", 1)[0]
    for field in STYLE_FIELDS:
        assert field in section, f"{style}: {field}"


def test_criteria_always_include_effort_cost_and_reversibility() -> None:
    text = (REFERENCES / "criteria.md").read_text()

    for criterion in ("Effort to build", "Running cost and operational burden", "Reversibility", "Testability", "Fit with the team"):
        assert criterion in text


def test_criteria_are_derived_from_the_quality_contexts() -> None:
    text = (REFERENCES / "criteria.md").read_text()

    for context in ("accessibility", "security by design", "privacy by design", "evolvability", "reliability"):
        assert context in text


def test_adr_template_has_the_standard_sections() -> None:
    text = (REFERENCES / "adr-template.md").read_text()

    for section in ("Status", "Context", "Options considered", "Decision", "Consequences", "Revisit when"):
        assert section in text


def test_example_shows_three_candidates_a_recommendation_and_a_trigger() -> None:
    text = (REFERENCES / "example.md").read_text()
    header = next(line for line in text.splitlines() if line.startswith("| Criterion"))

    assert len([c for c in header.split("|") if c.strip()]) == 4
    assert "**Recommendation:**" in text
    assert "**Would change the recommendation:**" in text


def test_skill_links_resolve() -> None:
    links = re.findall(r"\]\((references/[a-z-]+\.md)\)", _skill())

    assert links and all((SKILL / link).is_file() for link in links)


def test_skill_has_the_extended_steps() -> None:
    text = _skill()

    for required in (
        "riskiest assumption",
        "spike",
        "quality scenario",
        "existing tool",
        "sketch the threats",
        "exit plan",
        "first slice",
    ):
        assert required.lower() in text.lower(), required


def test_skill_steps_are_numbered_in_order_up_to_nine() -> None:
    numbers = [int(n) for n in re.findall(r"^(\d+)\. \*\*", _skill(), flags=re.MULTILINE)]

    assert numbers == list(range(1, 10))


def test_size_classes_use_signals_not_line_counts() -> None:
    text = (REFERENCES / "criteria.md").read_text()

    assert "500 lines" not in text
    assert "Signals" in text


def test_catalogue_lists_styles_not_recommended_by_default() -> None:
    text = (REFERENCES / "architectures.md").read_text()
    section = text.split("## Not recommended by default", 1)[1]

    for name in ("CQRS", "Event sourcing", "Service mesh", "Multi-cloud"):
        assert name in section


def test_adr_template_records_scenarios_exit_plan_and_riskiest_assumption() -> None:
    text = (REFERENCES / "adr-template.md").read_text()

    for section in ("Quality scenarios", "Exit plan", "Riskiest assumption"):
        assert section in text


def test_starting_a_project_defers_to_the_architecture_proposal() -> None:
    text = (REPO_ROOT / "skills" / "ai-rules-starting-a-project" / "SKILL.md").read_text()

    assert "ai-rules-architecture-proposal" in text
