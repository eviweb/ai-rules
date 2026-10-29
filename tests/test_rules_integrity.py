from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_language_rule_requires_english_for_project_artifacts():
    content = (REPO_ROOT / "rules" / "language.md").read_text()

    assert "English" in content
    assert "French" in content


def test_claude_entry_point_imports_only_existing_rule_files():
    entry_point = (REPO_ROOT / "agents" / "claude" / "CLAUDE.md").read_text()
    imported = [
        line.removeprefix("@rules/").strip()
        for line in entry_point.splitlines()
        if line.startswith("@rules/")
    ]

    missing = [name for name in imported if not (REPO_ROOT / "rules" / name).is_file()]

    assert missing == []


def test_rules_examples_do_not_use_unpinned_action_tags():
    unpinned = []
    for rule_file in sorted((REPO_ROOT / "rules").glob("*.md")):
        for number, line in enumerate(rule_file.read_text().splitlines(), start=1):
            if "uses:" in line and re.search(r"@v\d", line):
                unpinned.append(f"{rule_file.name}:{number}")

    assert unpinned == []


def test_rules_not_imported_by_claude_entry_point_are_marked_experimental():
    entry_point = (REPO_ROOT / "agents" / "claude" / "CLAUDE.md").read_text()
    orphans = [
        rule_file.name
        for rule_file in sorted((REPO_ROOT / "rules").glob("*.md"))
        if f"@rules/{rule_file.name}" not in entry_point
        and "Status: experimental" not in rule_file.read_text()
    ]

    assert orphans == []


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
