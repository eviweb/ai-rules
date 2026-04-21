from pathlib import Path

import pytest

from ai_rules.generator import (
    condense_content,
    generate_flat_file,
    resolve_imports,
    verify_flat_file,
)


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


def test_condense_content_removes_fenced_code_blocks() -> None:
    content = "# Rule\n\nDo this.\n\n```bash\necho hello\n```\n\nNot that.\n"
    result = condense_content(content)
    assert "echo hello" not in result
    assert "Do this." in result
    assert "Not that." in result


def test_condense_content_collapses_extra_blank_lines() -> None:
    content = "# Rule\n\n\n```bash\nfoo\n```\n\n\nNext section.\n"
    result = condense_content(content)
    assert "\n\n\n" not in result


def test_condense_content_keeps_inline_code() -> None:
    content = "Use `set -euo pipefail` at the top.\n"
    result = condense_content(content)
    assert "`set -euo pipefail`" in result


def test_condense_content_handles_multiple_fences() -> None:
    content = "A.\n\n```json\n{}\n```\n\nB.\n\n```yaml\nkey: val\n```\n\nC.\n"
    result = condense_content(content)
    assert "{}" not in result
    assert "key: val" not in result
    assert "A." in result
    assert "B." in result
    assert "C." in result


def test_condense_content_empty_input() -> None:
    assert condense_content("") == "\n"


def test_generate_flat_file_condense_strips_code_blocks(repo_root: Path) -> None:
    (repo_root / "rules" / "shell.md").write_text(
        "# Shell\n\nUse strict mode.\n\n```bash\nset -euo pipefail\n```\n"
    )
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/shell.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    generate_flat_file(repo_root, source, output, condense=True)
    text = output.read_text()
    assert "Use strict mode." in text
    assert "set -euo pipefail" not in text


def test_generate_flat_file_no_condense_keeps_code_blocks(repo_root: Path) -> None:
    (repo_root / "rules" / "shell.md").write_text(
        "# Shell\n\nUse strict mode.\n\n```bash\nset -euo pipefail\n```\n"
    )
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/shell.md\n")
    output = repo_root / "agents" / "claude" / "CLAUDE.md"
    generate_flat_file(repo_root, source, output, condense=False)
    assert "set -euo pipefail" in output.read_text()


def test_verify_flat_file_returns_true_when_in_sync(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    generate_flat_file(repo_root, source, output)
    assert verify_flat_file(repo_root, source, output) is True


def test_verify_flat_file_returns_false_when_stale(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    generate_flat_file(repo_root, source, output)
    (repo_root / "rules" / "language.md").write_text("# Language\n\nUpdated.\n")
    assert verify_flat_file(repo_root, source, output) is False


def test_verify_flat_file_returns_false_when_missing(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    assert verify_flat_file(repo_root, source, output) is False


def test_verify_flat_file_respects_condense_flag(repo_root: Path) -> None:
    (repo_root / "rules" / "shell.md").write_text(
        "# Shell\n\nUse strict mode.\n\n```bash\nset -euo pipefail\n```\n"
    )
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/shell.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    generate_flat_file(repo_root, source, output, condense=True)
    assert verify_flat_file(repo_root, source, output, condense=True) is True
    assert verify_flat_file(repo_root, source, output, condense=False) is False


def test_generate_flat_file_overwrites_existing(repo_root: Path) -> None:
    source = repo_root / "CLAUDE.md"
    source.write_text("@rules/language.md\n")
    output = repo_root / "agents" / "codex" / "AGENTS.md"
    output.parent.mkdir(parents=True)
    output.write_text("old content")
    generate_flat_file(repo_root, source, output)
    assert "old content" not in output.read_text()
    assert "# Language" in output.read_text()
