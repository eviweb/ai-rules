from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "ai-rules-quality-dimensions"
REFERENCES = SKILL / "references"
CONTEXTS = REFERENCES / "contexts"
DIMENSIONS = REFERENCES / "dimensions"
MAX_DIMENSION_BYTES = 2 * 1024
MAX_CONTEXT_BYTES = 4 * 1024

NEW_DIMENSIONS = ["Correctness", "Reliability", "Interoperability", "Safety", "Accessibility", "Evolvability"]
ISO_CHARACTERISTICS = [
    "Functional suitability", "Performance efficiency", "Compatibility",
    "Interaction capability", "Reliability", "Security", "Maintainability",
    "Flexibility", "Safety",
]


def _table_rows() -> list[tuple[str, str]]:
    """(dimension name, linked file stem) for each row of the SKILL.md table."""
    text = (SKILL / "SKILL.md").read_text()
    section = text.split("| Dimension |", 1)[1].split("\n\n", 1)[0]
    rows = []
    for line in section.splitlines()[2:]:
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip()
        match = re.match(r"\[(.+)\]\(references/dimensions/([a-z-]+)\.md\)", cell)
        assert match, f"row without a link: {line}"
        rows.append((match.group(1), match.group(2)))
    return rows


def _table_dimensions() -> list[str]:
    return [name for name, _ in _table_rows()]


def _dimension_files() -> set[str]:
    return {p.stem for p in DIMENSIONS.glob("*.md")}


def test_skill_lists_seventeen_dimensions() -> None:
    assert len(_table_dimensions()) == 17


def test_every_dimension_row_links_an_existing_file_and_the_reverse() -> None:
    linked = {stem for _, stem in _table_rows()}

    assert linked == _dimension_files()


def test_each_dimension_file_is_titled_with_its_dimension_and_stays_small() -> None:
    for name, stem in _table_rows():
        path = DIMENSIONS / f"{stem}.md"
        assert path.read_text().startswith(f"# {name}\n"), stem
        assert path.stat().st_size <= MAX_DIMENSION_BYTES, stem


def test_gemini_template_inlines_every_dimension_file() -> None:
    template = (REPO_ROOT / "agents" / "gemini" / "GEMINI.src.md").read_text()

    missing = [stem for stem in sorted(_dimension_files()) if f"references/dimensions/{stem}.md" not in template]
    assert missing == []


@pytest.mark.parametrize("dimension", NEW_DIMENSIONS)
def test_iso_additions_are_present(dimension: str) -> None:
    assert dimension in _table_dimensions()


def test_extensibility_is_replaced_by_evolvability() -> None:
    assert "Extensibility" not in _table_dimensions()
    assert "Evolvability" in _table_dimensions()


@pytest.mark.parametrize("characteristic", ISO_CHARACTERISTICS)
def test_iso_mapping_covers_every_characteristic(characteristic: str) -> None:
    assert characteristic in (REFERENCES / "iso-25010.md").read_text()


def test_iso_mapping_only_names_existing_dimensions() -> None:
    text = (REFERENCES / "iso-25010.md").read_text()
    table = [line for line in text.splitlines() if line.startswith("| ") and "ISO" not in line][1:]
    names = set()
    for line in table:
        names.update(part.strip() for part in line.split("|")[3].split(","))
    known = set(_table_dimensions())

    assert [n for n in names if n and n not in known] == []


def test_every_context_file_is_indexed_in_the_skill_and_the_reverse() -> None:
    on_disk = {p.stem for p in CONTEXTS.glob("*.md")}
    named = set(re.findall(r"references/contexts/([a-z-]+)\.md", (SKILL / "SKILL.md").read_text()))

    assert on_disk == named


@pytest.mark.parametrize("context_file", sorted(CONTEXTS.glob("*.md")), ids=lambda p: p.stem)
def test_context_file_states_when_to_read_it_and_stays_small(context_file: Path) -> None:
    text = context_file.read_text()

    assert "\nRead when" in text
    assert context_file.stat().st_size <= MAX_CONTEXT_BYTES


def test_dimension_files_point_to_their_context_files() -> None:
    expected = {
        "evolvability": "evolvability",
        "security": "security-by-design",
        "user-friendliness": "user-centric",
        "privacy": "privacy-by-design",
        "accessibility": "accessibility",
    }

    for stem, context in expected.items():
        assert f"contexts/{context}.md" in (DIMENSIONS / f"{stem}.md").read_text(), stem


def test_reliability_scales_the_practice_to_the_size_of_the_project() -> None:
    text = (DIMENSIONS / "reliability.md").read_text()

    for required in ("SLO", "runbook", "error budget", "Personal tool", "Public service"):
        assert required in text


def test_each_dimension_file_ends_with_red_flags() -> None:
    missing = [stem for stem in sorted(_dimension_files()) if "Red flags:" not in (DIMENSIONS / f"{stem}.md").read_text()]

    assert missing == []
