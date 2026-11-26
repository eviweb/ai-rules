from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "ai-rules-writing-documents"
REFERENCES = SKILL / "references"


def _skill() -> str:
    return (SKILL / "SKILL.md").read_text()


def _reference(name: str) -> str:
    return (REFERENCES / name).read_text()


def test_every_reference_linked_from_the_skill_exists() -> None:
    links = re.findall(r"\]\((references/[^)#]+)", _skill())

    assert links, "the skill links no reference"
    for link in links:
        assert (SKILL / link).is_file(), f"broken link: {link}"


@pytest.mark.parametrize(
    "reference",
    [
        "quality.md",
        "diagrams.md",
        "tooling.md",
        "types/spec.md",
        "types/design-doc.md",
        "types/readme.md",
        "types/guide.md",
    ],
)
def test_every_reference_is_linked_from_the_skill(reference: str) -> None:
    assert f"(references/{reference}" in _skill()


def test_skill_starts_from_the_reader_and_verifies_before_review() -> None:
    text = _skill()

    assert "reader and the purpose" in text
    assert text.index("**Verify.**") < text.index("**Review**")
    assert "Never invent" in text


def test_skill_defers_the_language_to_the_core_rule() -> None:
    text = _skill()

    assert "`core/language.md`" in text
    assert "`README.md`" in text


def test_quality_covers_changelog_practices_and_a_review_checklist() -> None:
    text = _reference("quality.md")

    assert "## Changelog" in text
    for practice in ("Written for users", "One line per entry", "breaking changes first", "Curated, not a commit dump"):
        assert practice in text
    assert "## Review checklist" in text


def test_spec_uses_ears_requirements_and_given_when_then_criteria() -> None:
    text = _reference("types/spec.md")

    assert "EARS" in text
    assert "Given" in text and "When" in text and "Then" in text
    assert "Non-goals" in text and "Open questions" in text


def test_guide_follows_the_four_diataxis_types() -> None:
    text = _reference("types/guide.md")

    for doc_type in ("Tutorial", "How-to guide", "Reference", "Explanation"):
        assert f"**{doc_type}**" in text


def test_diagrams_default_to_mermaid_with_c4_and_a_text_description() -> None:
    text = _reference("diagrams.md")

    assert "Mermaid" in text and "C4" in text
    assert "text description" in text


def test_changelog_rule_points_to_the_writing_practices() -> None:
    assert "ai-rules-writing-documents" in (REPO_ROOT / "rules" / "changelog.md").read_text()
