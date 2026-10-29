from __future__ import annotations

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
