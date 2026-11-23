from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from ai_rules.skills import (
    SkillFormatError,
    discover_skills,
    parse_frontmatter,
    verify_skill,
    verify_skills,
)

GOOD_DESCRIPTION = "Use when reviewing a change before commit or merge"


def write_skill(
    skills_dir: Path,
    name: str = "ai-rules-demo",
    *,
    frontmatter: str | None = None,
    body: str = "# Demo\n\nSteps.\n",
) -> Path:
    folder = skills_dir / name
    folder.mkdir(parents=True)
    if frontmatter is None:
        frontmatter = f"name: {name}\ndescription: {GOOD_DESCRIPTION}\n"
    (folder / "SKILL.md").write_text(f"---\n{frontmatter}---\n{body}")
    return folder


@pytest.fixture()
def skills_dir(tmp_path: Path) -> Path:
    path = tmp_path / "skills"
    path.mkdir()
    return path


# --- parse_frontmatter -------------------------------------------------------


def test_parse_frontmatter_reads_plain_and_quoted_scalars() -> None:
    text = "---\nname: demo\ndescription: \"Use when: quoted\"\nlicense: 'MIT'\n---\nbody"

    fields, body = parse_frontmatter(text)

    assert fields == {"name": "demo", "description": "Use when: quoted", "license": "MIT"}
    assert body == "body"


def test_parse_frontmatter_reads_nested_metadata() -> None:
    text = "---\nname: demo\nmetadata:\n  derived-from: superpowers/tdd\n  note: \"a: b\"\n---\n"

    fields, _ = parse_frontmatter(text)

    assert fields["metadata"] == {"derived-from": "superpowers/tdd", "note": "a: b"}


def test_parse_frontmatter_ignores_comments_and_blank_lines() -> None:
    fields, _ = parse_frontmatter("---\n# comment\n\nname: demo\n---\n")

    assert fields == {"name": "demo"}


@pytest.mark.parametrize(
    "text, message",
    [
        ("no frontmatter", "must start with"),
        ("---\nname: demo\n", "not closed"),
        ("---\nname: demo\nname: other\n---\n", "duplicate key"),
        ("---\njust text\n---\n", "line 2"),
        ("---\ndescription: Use when: unquoted colon\n---\n", "quote"),
        ("---\ndescription: a value # comment\n---\n", "quote"),
        ("---\ndescription: [a, b]\n---\n", "unsupported"),
        ("---\ndescription: >\n  folded\n---\n", "unsupported"),
        ('---\ndescription: "unterminated\n---\n', "quote"),
        ("---\nname: demo\n  indented: x\n---\n", "line 3"),
        ("---\nmetadata:\n  a: 1\n  a: 2\n---\n", "duplicate key"),
        ("---\nmetadata:\n    deep: x\n---\n", "line 3"),
    ],
)
def test_parse_frontmatter_rejects_invalid_or_unsupported_yaml(
    text: str, message: str
) -> None:
    with pytest.raises(SkillFormatError, match=message):
        parse_frontmatter(text)


# --- discover_skills ---------------------------------------------------------


def test_discover_skills_returns_every_directory_sorted(skills_dir: Path) -> None:
    write_skill(skills_dir, "ai-rules-b")
    write_skill(skills_dir, "ai-rules-a")
    (skills_dir / "README.md").write_text("index")

    assert [p.name for p in discover_skills(skills_dir)] == ["ai-rules-a", "ai-rules-b"]


def test_discover_skills_missing_directory_is_empty(tmp_path: Path) -> None:
    assert discover_skills(tmp_path / "absent") == []


# --- verify_skill: the happy path --------------------------------------------


def test_verify_skill_valid_skill_has_no_problem(skills_dir: Path) -> None:
    assert verify_skill(write_skill(skills_dir)) == []


# --- verify_skill: frontmatter -----------------------------------------------


def test_verify_skill_without_skill_md_is_reported(skills_dir: Path) -> None:
    folder = skills_dir / "ai-rules-empty"
    folder.mkdir()

    assert any("SKILL.md" in p for p in verify_skill(folder))


def test_verify_skill_invalid_yaml_is_reported(skills_dir: Path) -> None:
    folder = write_skill(skills_dir, frontmatter="description: Use when: bad\n")

    assert any("quote" in p for p in verify_skill(folder))


def test_verify_skill_name_must_match_folder(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        frontmatter=f"name: ai-rules-other\ndescription: {GOOD_DESCRIPTION}\n",
    )

    assert any("does not match folder" in p for p in verify_skill(folder))


def test_verify_skill_missing_name_or_description_is_reported(skills_dir: Path) -> None:
    folder = write_skill(skills_dir, frontmatter="license: MIT\n")

    problems = verify_skill(folder)

    assert any("name" in p and "missing" in p for p in problems)
    assert any("description" in p and "missing" in p for p in problems)


def test_verify_skill_requires_ai_rules_prefix(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        "bare-name",
        frontmatter=f"name: bare-name\ndescription: {GOOD_DESCRIPTION}\n",
    )

    assert any("prefix" in p for p in verify_skill(folder))


@pytest.mark.parametrize("name", ["ai-rules-Upper", "ai-rules-under_score", "ai-rules--x"])
def test_verify_skill_name_must_be_kebab_case(skills_dir: Path, name: str) -> None:
    folder = write_skill(
        skills_dir,
        name,
        frontmatter=f"name: {name}\ndescription: {GOOD_DESCRIPTION}\n",
    )

    assert any("kebab-case" in p for p in verify_skill(folder))


def test_verify_skill_name_longer_than_64_characters_is_reported(
    skills_dir: Path,
) -> None:
    name = "ai-rules-" + "a" * 60
    folder = write_skill(
        skills_dir,
        name,
        frontmatter=f"name: {name}\ndescription: {GOOD_DESCRIPTION}\n",
    )

    assert any("64" in p for p in verify_skill(folder))


def test_verify_skill_description_must_start_with_use_when(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        frontmatter="name: ai-rules-demo\ndescription: Reviews changes\n",
    )

    assert any("Use when" in p for p in verify_skill(folder))


def test_verify_skill_description_over_300_characters_is_reported(
    skills_dir: Path,
) -> None:
    long_description = "Use when " + "x" * 300
    folder = write_skill(
        skills_dir,
        frontmatter=f"name: ai-rules-demo\ndescription: {long_description}\n",
    )

    assert any("300" in p for p in verify_skill(folder))


def test_verify_skill_unknown_field_is_reported(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        frontmatter=(
            f"name: ai-rules-demo\ndescription: {GOOD_DESCRIPTION}\nmodel: opus\n"
        ),
    )

    assert any("unsupported field 'model'" in p for p in verify_skill(folder))


def test_verify_skill_metadata_must_be_a_mapping(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        frontmatter=(
            f"name: ai-rules-demo\ndescription: {GOOD_DESCRIPTION}\nmetadata: text\n"
        ),
    )

    assert any("metadata" in p and "mapping" in p for p in verify_skill(folder))


# --- verify_skill: size and references ---------------------------------------


def test_verify_skill_over_8_kib_is_reported(skills_dir: Path) -> None:
    folder = write_skill(skills_dir, body="x" * 8300)

    assert any("8 KiB" in p for p in verify_skill(folder))


def test_verify_skill_missing_referenced_file_is_reported(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        body="See [details](references/details.md) and `scripts/run.sh`.\n",
    )

    problems = verify_skill(folder)

    assert any("references/details.md" in p for p in problems)
    assert any("scripts/run.sh" in p for p in problems)


def test_verify_skill_existing_references_are_accepted(skills_dir: Path) -> None:
    folder = write_skill(
        skills_dir,
        body="See [details](references/details.md), [site](https://example.org), [top](#top).\n",
    )
    (folder / "references").mkdir()
    (folder / "references" / "details.md").write_text("details")

    assert verify_skill(folder) == []


def test_verify_skill_reference_escaping_the_folder_is_reported(
    skills_dir: Path,
) -> None:
    (skills_dir / "outside.md").write_text("x")
    folder = write_skill(skills_dir, body="See [x](../outside.md).\n")

    assert any("outside the skill folder" in p for p in verify_skill(folder))


# --- verify_skill: scripts ---------------------------------------------------


def _script(folder: Path, name: str, content: str, mode: int) -> Path:
    scripts = folder / "scripts"
    scripts.mkdir(exist_ok=True)
    path = scripts / name
    path.write_text(content)
    os.chmod(path, mode)
    return path


def test_verify_skill_non_executable_script_is_reported(skills_dir: Path) -> None:
    folder = write_skill(skills_dir)
    _script(folder, "run.sh", "#!/usr/bin/env bash\nset -euo pipefail\n", 0o644)

    assert any("not executable" in p for p in verify_skill(folder))


def test_verify_skill_shellcheck_failure_is_reported(skills_dir: Path) -> None:
    if shutil.which("shellcheck") is None:
        pytest.skip("shellcheck not installed")
    folder = write_skill(skills_dir)
    _script(folder, "run.sh", "#!/usr/bin/env bash\necho $UNQUOTED\n", 0o755)

    assert any("shellcheck" in p for p in verify_skill(folder))


def test_verify_skill_clean_script_is_accepted(skills_dir: Path) -> None:
    folder = write_skill(skills_dir)
    _script(folder, "run.sh", '#!/usr/bin/env bash\nset -euo pipefail\necho "ok"\n', 0o755)

    assert verify_skill(folder) == []


# --- verify_skill: derived-from ----------------------------------------------


DERIVED_FRONTMATTER = (
    "name: ai-rules-demo\n"
    f"description: {GOOD_DESCRIPTION}\n"
    "metadata:\n"
    "  derived-from: superpowers/demo @ abc123\n"
    "  license-of-origin: MIT\n"
)


def test_verify_skill_derived_from_requires_third_party_notice(
    skills_dir: Path, tmp_path: Path
) -> None:
    folder = write_skill(skills_dir, frontmatter=DERIVED_FRONTMATTER)

    problems = verify_skill(folder, repo_root=tmp_path)

    assert any("THIRD_PARTY.md" in p for p in problems)


def test_verify_skill_derived_from_requires_upstream_named_in_notice(
    skills_dir: Path, tmp_path: Path
) -> None:
    folder = write_skill(skills_dir, frontmatter=DERIVED_FRONTMATTER)
    (tmp_path / "THIRD_PARTY.md").write_text("# Third party\n\nSomething else.\n")

    problems = verify_skill(folder, repo_root=tmp_path)

    assert any("superpowers" in p for p in problems)


def test_verify_skill_derived_from_requires_license_of_origin(
    skills_dir: Path, tmp_path: Path
) -> None:
    folder = write_skill(
        skills_dir,
        frontmatter=(
            "name: ai-rules-demo\n"
            f"description: {GOOD_DESCRIPTION}\n"
            "metadata:\n  derived-from: superpowers/demo\n"
        ),
    )
    (tmp_path / "THIRD_PARTY.md").write_text("superpowers (MIT)\n")

    assert any("license-of-origin" in p for p in verify_skill(folder, repo_root=tmp_path))


def test_verify_skill_derived_from_with_notice_is_accepted(
    skills_dir: Path, tmp_path: Path
) -> None:
    folder = write_skill(skills_dir, frontmatter=DERIVED_FRONTMATTER)
    (tmp_path / "THIRD_PARTY.md").write_text("## superpowers\n\nMIT License\n")

    assert verify_skill(folder, repo_root=tmp_path) == []


# --- verify_skills -----------------------------------------------------------


def test_verify_skills_maps_only_invalid_skills_to_their_problems(
    skills_dir: Path,
) -> None:
    write_skill(skills_dir, "ai-rules-good")
    write_skill(skills_dir, "ai-rules-bad", frontmatter="name: ai-rules-bad\n")

    result = verify_skills(skills_dir)

    assert list(result) == ["ai-rules-bad"]
    assert result["ai-rules-bad"]
