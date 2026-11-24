from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-sources-age.sh"
REGISTER = REPO_ROOT / "docs" / "sources.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "sources-review.yml"

HEADER = "| Source | Version used | Reference | Verified | Every (months) | Status | Cited in |\n|---|---|---|---|---|---|---|\n"


def write_register(tmp_path: Path, *rows: str) -> Path:
    path = tmp_path / "sources.md"
    path.write_text("# Register\n\n" + HEADER + "".join(rows))
    return path


def row(name: str, verified: str, every: int, version: str = "1", status: str = "verified") -> str:
    return f"| {name} | {version} | https://example.org | {verified} | {every} | {status} | test |\n"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), *args], capture_output=True, text=True, check=False)


def test_fresh_sources_are_not_due(tmp_path: Path) -> None:
    register = write_register(tmp_path, row("Alpha", "2026-11-01", 12))

    result = run("--file", str(register), "--today", "2026-12-01")

    assert result.returncode == 0
    assert "up to date" in result.stdout


def test_a_source_past_its_review_period_is_due(tmp_path: Path) -> None:
    register = write_register(tmp_path, row("Alpha", "2025-11-01", 12), row("Beta", "2026-11-01", 12))

    result = run("--file", str(register), "--today", "2026-11-24")

    assert result.returncode == 1
    assert "Alpha" in result.stdout and "Beta" not in result.stdout
    assert "review was due 2026-11-01" in result.stdout


def test_the_review_date_itself_counts_as_due(tmp_path: Path) -> None:
    register = write_register(tmp_path, row("Alpha", "2026-05-24", 6))

    assert run("--file", str(register), "--today", "2026-11-24").returncode == 1
    assert run("--file", str(register), "--today", "2026-11-23").returncode == 0


def test_a_source_never_verified_is_due(tmp_path: Path) -> None:
    register = write_register(tmp_path, row("Gamma", "never", 12, status="not checked"))

    result = run("--file", str(register), "--today", "2026-11-24")

    assert result.returncode == 1
    assert "Gamma" in result.stdout and "never verified" in result.stdout


def test_upstream_that_moved_is_reported(tmp_path: Path) -> None:
    register = write_register(tmp_path, row("Superpowers (obra/superpowers)", "2026-11-24", 3, version="v7.0.2 @ 22f0b46"))

    moved = run("--file", str(register), "--today", "2026-11-25", "--check-upstream", "--latest-upstream", "abcdef1234")
    same = run("--file", str(register), "--today", "2026-11-25", "--check-upstream", "--latest-upstream", "22f0b463e7a5e579904dd6211a520321035526f7")

    assert moved.returncode == 1 and "upstream moved from 22f0b46 to abcdef1" in moved.stdout
    assert same.returncode == 0


def test_upstream_check_without_a_pinned_commit_is_an_error(tmp_path: Path) -> None:
    register = write_register(tmp_path, row("Alpha", "2026-11-01", 12))

    result = run("--file", str(register), "--check-upstream", "--latest-upstream", "abc1234")

    assert result.returncode == 2
    assert "no pinned Superpowers commit" in result.stderr


def test_invalid_input_exits_with_code_2(tmp_path: Path) -> None:
    assert run("--file", str(tmp_path / "missing.md")).returncode == 2
    assert run("--today", "tomorrow").returncode == 2
    assert run("--unknown").returncode == 2
    bad = write_register(tmp_path, row("Alpha", "2026-11-01", 0).replace("| 0 |", "| soon |"))
    assert run("--file", str(bad)).returncode == 2


def test_help_and_version_exit_zero() -> None:
    assert "Usage:" in run("--help").stdout
    assert "check-sources-age.sh" in run("--version").stdout


def test_the_real_register_parses_and_every_row_has_a_valid_period() -> None:
    result = run("--file", str(REGISTER), "--today", "2026-11-24")

    assert result.returncode in (0, 1)
    assert "Error" not in result.stderr


def test_register_rows_have_the_seven_columns() -> None:
    rows = [line for line in REGISTER.read_text().splitlines() if line.startswith("| ") and "---" not in line][1:]

    assert rows
    for line in rows:
        assert len(line.strip().strip("|").split("|")) == 7, line


CITED_PATTERNS = {
    "WCAG": r"WCAG",
    "RGAA": r"RGAA",
    "EN 301 549": r"EN 301 549",
    "European Accessibility Act": r"Accessibility Act|2019/882",
    "Section 508": r"Section 508",
    "GDPR": r"GDPR",
    "Cavoukian": r"Cavoukian",
    "OWASP Top 10": r"OWASP Top 10",
    "ASVS": r"ASVS",
    "Saltzer": r"Saltzer",
    "Shostack": r"Shostack",
    "SLSA": r"SLSA",
    "ISO/IEC 25010": r"ISO/IEC 25010",
    "ISO 9241": r"ISO 9241",
    "Nielsen": r"Nielsen",
    "DORA": r"DORA",
}


@pytest.mark.parametrize("name", sorted(CITED_PATTERNS))
def test_every_standard_cited_in_the_skills_has_a_register_entry(name: str) -> None:
    skills_text = "\n".join(p.read_text() for p in (REPO_ROOT / "skills").rglob("*.md"))

    if re.search(CITED_PATTERNS[name], skills_text):
        assert name.lower() in REGISTER.read_text().lower(), f"{name} is cited in skills/ but missing from docs/sources.md"


def test_the_register_pins_the_same_superpowers_commit_as_the_derived_skills() -> None:
    register = REGISTER.read_text()
    pin = re.search(r"Superpowers[^\n]*@ ([0-9a-f]{7})", register)
    assert pin
    derived = "\n".join(p.read_text() for p in (REPO_ROOT / "skills").glob("*/SKILL.md") if "derived-from" in p.read_text())

    assert set(re.findall(r"superpowers/[a-z-]+ @ ([0-9a-f]+)", derived)) == {pin.group(1)}


def test_the_workflow_runs_monthly_and_can_be_started_by_hand() -> None:
    text = WORKFLOW.read_text()

    assert re.search(r'cron: "\d+ \d+ 1 \* \*"', text)
    assert "workflow_dispatch:" in text


def test_the_workflow_follows_the_ci_rules() -> None:
    text = WORKFLOW.read_text()

    assert "pull_request_target" not in text
    assert "contents: read" in text and "issues: write" in text
    assert "persist-credentials: false" in text
    assert "timeout-minutes:" in text and "concurrency:" in text
    uses = re.findall(r"uses: ([^\s]+)", text)
    assert uses and all(re.fullmatch(r".+@[0-9a-f]{40}", u) for u in uses), uses


def test_the_workflow_opens_one_issue_and_does_not_block_merges() -> None:
    text = WORKFLOW.read_text()

    assert "gh issue create" in text
    assert "gh issue list" in text
    assert "check-sources-age.sh --check-upstream" in text
    assert "pull_request:" not in text and "push:" not in text
