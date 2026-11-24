from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_language_rule_requires_english_for_project_artifacts():
    content = (REPO_ROOT / "core" / "language.md").read_text()

    assert "English" in content
    assert "French" in content


ENTRY_POINT = REPO_ROOT / "agents" / "claude" / "CLAUDE.md"


def _imported_files(entry_point: Path) -> list[Path]:
    """Files an entry point imports, resolved the way Claude Code does it.

    Claude Code resolves a relative ``@import`` against the real path of the
    file that holds it (``~/.claude/CLAUDE.md`` is a symlink into this repo).
    """
    return [
        (entry_point.parent / line.removeprefix("@").strip()).resolve()
        for line in entry_point.read_text().splitlines()
        if line.startswith("@")
    ]


def test_claude_entry_point_imports_resolve_from_its_real_path():
    unresolved = [str(path) for path in _imported_files(ENTRY_POINT) if not path.is_file()]

    assert unresolved == []


def test_rules_examples_do_not_use_unpinned_action_tags():
    unpinned = []
    for rule_file in sorted((REPO_ROOT / "rules").glob("*.md")):
        for number, line in enumerate(rule_file.read_text().splitlines(), start=1):
            if "uses:" in line and re.search(r"@v\d", line):
                unpinned.append(f"{rule_file.name}:{number}")

    assert unpinned == []


def test_claude_entry_point_imports_exactly_the_core_files():
    imported = sorted(path for path in _imported_files(ENTRY_POINT))
    core_files = sorted(f.resolve() for f in (REPO_ROOT / "core").glob("*.md"))

    assert imported == core_files


def test_scoped_rules_are_not_imported_because_an_import_always_loads_the_file():
    rules_dir = (REPO_ROOT / "rules").resolve()
    imported_rules = [p for p in _imported_files(ENTRY_POINT) if p.is_relative_to(rules_dir)]

    assert imported_rules == []


def _paths_of(rule_file: Path) -> list[str]:
    from ai_rules.generator import split_frontmatter

    return split_frontmatter(rule_file.read_text())[0]


def test_every_scoped_rule_declares_paths():
    without_paths = [
        f.name for f in sorted((REPO_ROOT / "rules").glob("*.md")) if not _paths_of(f)
    ]

    assert without_paths == []


def test_scoped_rules_stay_within_their_size_budget():
    too_big = [
        f"{f.name} ({f.stat().st_size} bytes)"
        for f in sorted((REPO_ROOT / "rules").glob("*.md"))
        if f.stat().st_size > 6 * 1024
    ]

    assert too_big == []


def test_core_files_have_no_paths_because_they_are_always_loaded():
    scoped_core = [f.name for f in (REPO_ROOT / "core").glob("*.md") if _paths_of(f)]

    assert scoped_core == []


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
    pr = (
        REPO_ROOT / "skills" / "ai-rules-pull-requests-and-issues" / "SKILL.md"
    ).read_text()
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


def test_cli_rule_exempts_internal_read_only_helper_scripts():
    cli_rule = (REPO_ROOT / "rules" / "cli.md").read_text()

    assert "user-facing" in cli_rule
    assert "internal" in cli_rule and "read-only" in cli_rule
    assert "`-h|--help`" in cli_rule


def test_tdd_rule_makes_the_refactor_step_explicit_and_points_to_the_skill():
    tdd_rule = (REPO_ROOT / "rules" / "tdd.md").read_text()

    assert "TDD is mandatory" in tdd_rule
    assert "Refactor" in tdd_rule and "nothing to refactor" in tdd_rule
    assert "ai-rules-test-driven-development" in tdd_rule
    assert "ai-rules-refactoring-and-design" in tdd_rule


def test_tdd_rule_limits_the_mandate_to_code_with_testable_behavior():
    tdd_rule = (REPO_ROOT / "rules" / "tdd.md").read_text()

    assert "testable behavior" in tdd_rule
    assert "ai-rules-verification-before-completion" in tdd_rule


def test_core_scopes_refactoring_to_the_current_change_and_asks_to_report_the_rest():
    principles = (REPO_ROOT / "core" / "principles.md").read_text()

    assert "outside the current change" in principles
    assert "Refactor step of TDD" in principles
    assert "report it" in principles


def test_core_asks_to_find_why_code_exists_before_removing_it():
    principles = (REPO_ROOT / "core" / "principles.md").read_text()

    assert "find out why it exists" in principles


def test_tdd_rule_scopes_the_refactor_step_to_the_code_the_cycle_touches():
    tdd_rule = (REPO_ROOT / "rules" / "tdd.md").read_text()

    assert "writes or modifies" in tdd_rule
    assert "immediate surroundings" not in tdd_rule
