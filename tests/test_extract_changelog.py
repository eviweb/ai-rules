from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "skills" / "ai-rules-releasing" / "scripts" / "extract-changelog.sh"

CHANGELOG = """# Changelog

## [Unreleased]

### Added

- Something not released yet

## [1.0.0-rc.1] - 2026-02-01

### Fixed

- Release candidate fix

## [0.9.0] - 2026-01-15

Release summary of 0.9.0.

### Added

- Feature A
- Feature B

## [0.8.0] - 2025-12-01

### Changed

- Older change
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "CHANGELOG.md").write_text(CHANGELOG)
    return tmp_path


def run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True, check=False)


def test_extracts_only_the_requested_section_without_surrounding_blank_lines(project: Path) -> None:
    result = run(project, "0.9.0")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "Release summary of 0.9.0.\n\n### Added\n\n- Feature A\n- Feature B\n"


def test_matches_pre_release_versions_literally(project: Path) -> None:
    result = run(project, "1.0.0-rc.1")

    assert result.stdout == "### Fixed\n\n- Release candidate fix\n"


def test_reads_another_changelog_with_the_changelog_option(project: Path, tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = run(elsewhere, "--changelog", str(project / "CHANGELOG.md"), "0.8.0")

    assert result.stdout == "### Changed\n\n- Older change\n"


def test_unknown_version_fails_with_a_message(project: Path) -> None:
    result = run(project, "9.9.9")

    assert result.returncode == 1
    assert "[9.9.9] not found" in result.stderr


def test_missing_changelog_fails_with_a_message(tmp_path: Path) -> None:
    result = run(tmp_path, "1.0.0")

    assert result.returncode == 1
    assert "changelog not found" in result.stderr


def test_missing_version_argument_fails(project: Path) -> None:
    assert run(project).returncode == 1


def test_version_option_does_not_depend_on_a_version_file(project: Path) -> None:
    result = run(project, "-V")

    assert result.returncode == 0
    assert "unknown" not in result.stdout


def test_the_script_lives_only_in_the_skill() -> None:
    assert not (REPO_ROOT / "scripts" / "extract-changelog.sh").exists()
