from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_language_rule_requires_english_for_project_artifacts():
    content = (REPO_ROOT / "core" / "language.md").read_text()

    assert "English" in content
    assert "French" in content


def test_claude_entry_point_imports_only_existing_rule_files():
    entry_point = (REPO_ROOT / "agents" / "claude" / "CLAUDE.md").read_text()
    imported = [
        line.removeprefix("@").strip()
        for line in entry_point.splitlines()
        if line.startswith(("@rules/", "@core/"))
    ]

    missing = [name for name in imported if not (REPO_ROOT / name).is_file()]

    assert missing == []


def test_rules_examples_do_not_use_unpinned_action_tags():
    unpinned = []
    for rule_file in sorted((REPO_ROOT / "rules").glob("*.md")):
        for number, line in enumerate(rule_file.read_text().splitlines(), start=1):
            if "uses:" in line and re.search(r"@v\d", line):
                unpinned.append(f"{rule_file.name}:{number}")

    assert unpinned == []


def test_every_core_and_rules_file_is_imported_by_claude_entry_point():
    entry_point = (REPO_ROOT / "agents" / "claude" / "CLAUDE.md").read_text()
    not_imported = [
        f"{directory}/{rule_file.name}"
        for directory in ("core", "rules")
        for rule_file in sorted((REPO_ROOT / directory).glob("*.md"))
        if f"@{directory}/{rule_file.name}" not in entry_point
    ]

    assert not_imported == []


def test_core_stays_within_its_budget():
    core_files = sorted((REPO_ROOT / "core").glob("*.md"))
    total_bytes = sum(f.stat().st_size for f in core_files)
    total_lines = sum(len(f.read_text().splitlines()) for f in core_files)

    assert total_bytes <= 10 * 1024
    assert total_lines <= 200


def test_core_files_are_not_duplicated_in_rules():
    duplicated = [
        f.name for f in (REPO_ROOT / "core").glob("*.md") if (REPO_ROOT / "rules" / f.name).exists()
    ]

    assert duplicated == []


def test_ci_rule_points_to_existing_trigger_template():
    ci_rule = (REPO_ROOT / "rules" / "ci.md").read_text()

    assert "templates/ci-triggers.md" in ci_rule
    assert (REPO_ROOT / "templates" / "ci-triggers.md").is_file()


def test_package_version_matches_version_file():
    from ai_rules import __version__

    assert __version__ == (REPO_ROOT / "VERSION").read_text().strip()


def test_package_version_falls_back_to_version_file_when_not_installed(monkeypatch):
    import importlib
    import importlib.metadata

    import ai_rules

    def raise_not_found(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", raise_not_found)
    try:
        reloaded = importlib.reload(ai_rules)

        assert reloaded.__version__ == (REPO_ROOT / "VERSION").read_text().strip()
    finally:
        monkeypatch.undo()
        importlib.reload(ai_rules)


def test_rules_forbid_attribution_lines_in_every_published_message():
    commits = (REPO_ROOT / "core" / "commits.md").read_text()
    pr = (REPO_ROOT / "rules" / "pr.md").read_text()
    release = (REPO_ROOT / "rules" / "release.md").read_text()

    assert "No attribution" in commits
    assert "Co-Authored-By" in commits
    assert "tag messages" in commits and "release notes" in commits
    assert "attribution" in pr.lower()
    assert "attribution" in release.lower()


def test_attribution_rule_names_no_specific_tool():
    commits = (REPO_ROOT / "core" / "commits.md").read_text()
    section = commits.split("No attribution", 1)[1].split("\n", 3)[0]

    assert "Claude" not in section
