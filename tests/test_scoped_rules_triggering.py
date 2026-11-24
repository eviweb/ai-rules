"""Which scoped rules a Claude Code session loads when it touches a file.

Measured on 2026-11-24 (docs/metrics/0.8.0.md): scoped rules arrive as a
system reminder when a matching file is read, and cost more than the file
itself. These tests pin the triggers and bound the cost of common files.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ai_rules.generator import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / "rules"

# Budget in bytes of the rules loaded by reading one file of that kind.
SHELL_SCRIPT_BUDGET = 12 * 1024
CHANGELOG_BUDGET = 7 * 1024


def _expand_braces(pattern: str) -> list[str]:
    match = re.search(r"\{([^{}]*)\}", pattern)
    if match is None:
        return [pattern]
    head, tail = pattern[: match.start()], pattern[match.end() :]
    return [
        expanded
        for option in match.group(1).split(",")
        for expanded in _expand_braces(head + option + tail)
    ]


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    out = ""
    i = 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif glob.startswith("**", i):
            out += ".*"
            i += 2
        elif glob[i] == "*":
            out += "[^/]*"
            i += 1
        else:
            out += re.escape(glob[i])
            i += 1
    return re.compile(f"^{out}$")


def rules_loaded_by(path: str) -> dict[str, int]:
    """Scoped rules whose ``paths:`` match *path*, with their size in bytes."""
    loaded: dict[str, int] = {}
    for rule in sorted(RULES_DIR.glob("*.md")):
        globs = [g for p in split_frontmatter(rule.read_text())[0] for g in _expand_braces(p)]
        if any(_glob_to_regex(g).match(path) for g in globs):
            loaded[rule.stem] = rule.stat().st_size
    return loaded


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("scripts/measure-context.sh", {"shell", "cli", "naming", "error-handling"}),
        (".github/workflows/ci.yml", {"ci", "compatibility"}),
        ("CHANGELOG.md", {"docs", "changelog", "versioning"}),
        ("VERSION", {"docs", "changelog", "versioning", "release"}),
        ("src/ai_rules/cli.py", {"cli", "naming", "error-handling", "logging"}),
        ("pyproject.toml", {"dependencies", "compatibility"}),
    ],
)
def test_file_loads_exactly_the_expected_rules(path: str, expected: set[str]) -> None:
    assert set(rules_loaded_by(path)) == expected


def test_reading_a_shell_script_stays_within_its_rule_budget() -> None:
    assert sum(rules_loaded_by("scripts/some-script.sh").values()) <= SHELL_SCRIPT_BUDGET


def test_reading_the_changelog_stays_within_its_rule_budget() -> None:
    assert sum(rules_loaded_by("CHANGELOG.md").values()) <= CHANGELOG_BUDGET


def test_application_logging_is_not_loaded_for_shell_scripts() -> None:
    assert "logging" not in rules_loaded_by("scripts/some-script.sh")


def test_release_workflow_is_not_loaded_by_reading_the_changelog() -> None:
    assert "release" not in rules_loaded_by("CHANGELOG.md")
