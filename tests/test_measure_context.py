from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "measure-context.sh"


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    (tmp_path / "agents" / "claude").mkdir(parents=True)
    (tmp_path / "agents" / "codex").mkdir(parents=True)
    (tmp_path / "agents" / "gemini").mkdir(parents=True)
    (tmp_path / "rules" / "a.md").write_text("a" * 400)
    (tmp_path / "rules" / "b.md").write_text("b" * 800)
    (tmp_path / "rules" / "orphan.md").write_text("o" * 200)
    (tmp_path / "agents" / "claude" / "CLAUDE.md").write_text("@rules/a.md\n@rules/b.md\n")
    (tmp_path / "agents" / "gemini" / "GEMINI.md").write_text("@./rules/a.md\n")
    (tmp_path / "agents" / "codex" / "AGENTS.md").write_text("c" * 1000)
    return tmp_path


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), *args], capture_output=True, text=True, check=False)


def test_measure_context_prints_markdown_table_with_layers(sample_repo):
    result = run_script("--root", str(sample_repo))

    assert result.returncode == 0
    assert "| Layer | Files | Bytes | Lines | ~Tokens |" in result.stdout
    assert "| Claude Code @imports | 3 |" in result.stdout
    assert "| rules/ directory | 3 |" in result.stdout
    assert "| Codex flat file | 1 | 1000 |" in result.stdout


def test_measure_context_counts_import_bytes_and_approximate_tokens(sample_repo):
    result = run_script("--root", str(sample_repo))

    imports_row = next(line for line in result.stdout.splitlines() if "Claude Code @imports" in line)
    cells = [cell.strip() for cell in imports_row.strip("|").split("|")]
    assert cells[2] == str(len("@rules/a.md\n@rules/b.md\n") + 400 + 800)
    assert cells[4] == str(-(-int(cells[2]) * 10 // 27))


def test_measure_context_bytes_per_token_option_overrides_calibration(sample_repo):
    result = run_script("--root", str(sample_repo), "--bytes-per-token", "4")

    imports_row = next(line for line in result.stdout.splitlines() if "Claude Code @imports" in line)
    cells = [cell.strip() for cell in imports_row.strip("|").split("|")]
    assert cells[4] == str(-(-int(cells[2]) // 4))


def test_measure_context_rejects_invalid_bytes_per_token(sample_repo):
    result = run_script("--root", str(sample_repo), "--bytes-per-token", "abc")

    assert result.returncode == 2
    assert "Error: --bytes-per-token must be a positive number" in result.stderr


def test_measure_context_reports_overlapping_files(sample_repo):
    result = run_script("--root", str(sample_repo))

    assert "Overlap: 2 files" in result.stdout
    assert "Claude Code loads each once" in result.stdout
    assert "orphan.md" not in result.stdout.split("Overlap")[1]


def test_measure_context_files_option_lists_each_rule_file(sample_repo):
    result = run_script("--root", str(sample_repo), "--files")

    assert "| rules/a.md |" in result.stdout
    assert "| rules/orphan.md |" in result.stdout


def test_measure_context_skips_layers_that_do_not_exist(sample_repo):
    result = run_script("--root", str(sample_repo))

    assert "core/" not in result.stdout
    assert "skills/" not in result.stdout


def test_measure_context_includes_core_and_skills_layers_when_present(sample_repo):
    (sample_repo / "core").mkdir()
    (sample_repo / "core" / "language.md").write_text("x" * 100)
    (sample_repo / "skills" / "demo").mkdir(parents=True)
    (sample_repo / "skills" / "demo" / "SKILL.md").write_text("y" * 50)

    result = run_script("--root", str(sample_repo))

    assert "| core/ | 1 | 100 |" in result.stdout
    assert "| skills/ | 1 | 50 |" in result.stdout


def test_measure_context_unknown_root_exits_with_error(tmp_path):
    result = run_script("--root", str(tmp_path / "missing"))

    assert result.returncode == 2
    assert "Error: root directory not found" in result.stderr


def test_measure_context_help_exits_zero():
    result = run_script("--help")

    assert result.returncode == 0
    assert "Usage:" in result.stdout
