from pathlib import Path

import pytest

from ai_rules.generator import generate_flat_file, resolve_imports


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    rules = root / "rules"
    rules.mkdir()
    (rules / "language.md").write_text("# Language\n\nWrite in English.\n")
    (rules / "principles.md").write_text("# Principles\n\nKeep it simple.\n")
    return root


def test_resolve_imports_inlines_rule_file(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("# Rules\n\n@rules/language.md\n")
    result = resolve_imports(source, repo_root)
    assert "# Language" in result
    assert "Write in English." in result
    assert "@rules/language.md" not in result


def test_resolve_imports_multiple_files(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n@rules/principles.md\n")
    result = resolve_imports(source, repo_root)
    assert "Write in English." in result
    assert "Keep it simple." in result


def test_resolve_imports_preserves_non_import_lines(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("# Title\n\nSome text.\n\n@rules/language.md\n")
    result = resolve_imports(source, repo_root)
    assert "# Title" in result
    assert "Some text." in result


def test_resolve_imports_empty_source(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("")
    result = resolve_imports(source, repo_root)
    assert result == "\n"


def test_generate_flat_file_writes_output(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    generate_flat_file(repo_root, source, output)
    assert output.exists()
    assert "# Language" in output.read_text()


def test_generate_flat_file_creates_parent_dirs(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "deep" / "nested" / "AGENTS.md"
    generate_flat_file(repo_root, source, output)
    assert output.exists()


def test_generate_flat_file_overwrites_existing(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    output.parent.mkdir(parents=True)
    output.write_text("old content")
    generate_flat_file(repo_root, source, output)
    assert "old content" not in output.read_text()
    assert "# Language" in output.read_text()
