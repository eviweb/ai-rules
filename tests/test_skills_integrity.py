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


def _derived_from_values() -> list[tuple[str, str]]:
    from ai_rules.skills import discover_skills, parse_frontmatter

    values = []
    for folder in discover_skills(REPO_ROOT / "skills"):
        fields, _ = parse_frontmatter((folder / "SKILL.md").read_text())
        metadata = fields.get("metadata", {})
        if isinstance(metadata, dict) and "derived-from" in metadata:
            values.append((folder.name, metadata["derived-from"]))
    return values


def test_third_party_notice_carries_the_upstream_mit_license() -> None:
    notice = (REPO_ROOT / "THIRD_PARTY.md").read_text()

    assert "obra/superpowers" in notice
    assert "MIT License" in notice
    assert "Copyright (c) 2025 Jesse Vincent" in notice
    assert "Permission is hereby granted, free of charge" in notice


def test_derived_skills_pin_the_upstream_version_they_were_written_from() -> None:
    unpinned = [name for name, value in _derived_from_values() if " @ " not in value]

    assert unpinned == []


def test_derived_skills_declare_the_license_of_origin() -> None:
    from ai_rules.skills import discover_skills, parse_frontmatter

    for folder in discover_skills(REPO_ROOT / "skills"):
        fields, _ = parse_frontmatter((folder / "SKILL.md").read_text())
        metadata = fields.get("metadata", {})
        if isinstance(metadata, dict) and "derived-from" in metadata:
            assert metadata.get("license-of-origin") == "MIT", folder.name


SKILL_LISTING_BUDGET_BYTES = 5 * 1024


def test_skill_listing_stays_within_its_always_on_budget() -> None:
    """Name and description of every skill sit in the agent's context at every turn."""
    from ai_rules.skills import discover_skills, parse_frontmatter

    listing_bytes = 0
    for folder in discover_skills(REPO_ROOT / "skills"):
        fields, _ = parse_frontmatter((folder / "SKILL.md").read_text())
        listing_bytes += len(f"{fields['name']}{fields['description']}".encode())

    assert listing_bytes <= SKILL_LISTING_BUDGET_BYTES, (
        f"skill listing is {listing_bytes} bytes, budget {SKILL_LISTING_BUDGET_BYTES}: "
        "shorten descriptions or merge skills"
    )
