from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules import __version__
from ai_rules.cli import app

RUNNER = CliRunner()

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

REAL_REPO = Path(__file__).parent.parent


def _agents_toml(install_root: Path) -> str:
    """agents.toml identical to the real one but with install_dirs in tmp."""
    return f"""
[agents.claude]
name             = "Claude Code"
entry_point      = "agents/claude/CLAUDE.md"
install_dir      = "{install_root}/claude"
supports_imports = true

  [[agents.claude.links]]
  source = "agents/claude/CLAUDE.md"
  target = "CLAUDE.md"

  [[agents.claude.links]]
  source = "rules"
  target = "rules"

  [[agents.claude.links]]
  source = "settings.json"
  target = "settings.json"

[agents.codex]
name               = "Codex"
entry_point        = "agents/codex/AGENTS.md"
install_dir        = "{install_root}/codex"
supports_imports   = false
condense_flat_file = false

  [[agents.codex.links]]
  source = "agents/codex/AGENTS.md"
  target = "AGENTS.md"

  [[agents.codex.config_patches]]
  file  = "config.toml"
  key   = "project_doc_max_bytes"
  value = 131072

[agents.gemini]
name             = "Gemini"
entry_point      = "agents/gemini/GEMINI.md"
install_dir      = "{install_root}/gemini"
supports_imports = true

  [[agents.gemini.links]]
  source = "agents/gemini/GEMINI.md"
  target = "GEMINI.md"

  [[agents.gemini.links]]
  source = "rules"
  target = "rules"
"""


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """Minimal repo wired to tmp install dirs, real rules/agents content copied."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    install_root = tmp_path / "install"
    install_root.mkdir()

    (repo_root / "agents.toml").write_text(_agents_toml(install_root))
    shutil.copytree(REAL_REPO / "rules", repo_root / "rules")
    shutil.copytree(REAL_REPO / "agents", repo_root / "agents")
    if (REAL_REPO / "settings.json").exists():
        shutil.copy2(REAL_REPO / "settings.json", repo_root / "settings.json")

    return repo_root


def invoke(args: list[str], repo: Path) -> object:
    return RUNNER.invoke(app, args, env={"AI_RULES_HOME": str(repo)})


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------


def test_version(repo: Path) -> None:
    result = invoke(["--version"], repo)
    assert result.exit_code == 0
    assert __version__ in result.output


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_shows_all_agents(repo: Path) -> None:
    result = invoke(["list"], repo)
    assert result.exit_code == 0
    assert "claude" in result.output
    assert "codex" in result.output
    assert "gemini" in result.output


def test_list_labels_import_mode(repo: Path) -> None:
    result = invoke(["list"], repo)
    assert "native imports" in result.output
    assert "generated flat file" in result.output


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def test_status_all_agents_not_installed(repo: Path) -> None:
    result = invoke(["status"], repo)
    assert result.exit_code == 0
    assert "[claude]" in result.output
    assert "[codex]" in result.output
    assert "[gemini]" in result.output
    assert "not installed" in result.output


def test_status_single_agent(repo: Path) -> None:
    result = invoke(["status", "codex"], repo)
    assert result.exit_code == 0
    assert "[codex]" in result.output
    assert "[claude]" not in result.output
    assert "[gemini]" not in result.output


def test_status_shows_ok_after_install(repo: Path) -> None:
    invoke(["install"], repo)
    result = invoke(["status"], repo)
    assert "ok" in result.output


def test_status_unknown_agent_exits_1(repo: Path) -> None:
    result = invoke(["status", "unknown"], repo)
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------


def test_install_all_agents_creates_symlinks(repo: Path, tmp_path: Path) -> None:
    result = invoke(["install"], repo)
    assert result.exit_code == 0
    assert "Done." in result.output
    assert (tmp_path / "install" / "claude" / "CLAUDE.md").is_symlink()
    assert (tmp_path / "install" / "codex" / "AGENTS.md").is_symlink()
    assert (tmp_path / "install" / "gemini" / "GEMINI.md").is_symlink()


def test_install_single_agent(repo: Path, tmp_path: Path) -> None:
    result = invoke(["install", "codex"], repo)
    assert result.exit_code == 0
    assert (tmp_path / "install" / "codex" / "AGENTS.md").is_symlink()
    assert not (tmp_path / "install" / "claude" / "CLAUDE.md").exists()


def test_install_dry_run_makes_no_changes(repo: Path, tmp_path: Path) -> None:
    result = invoke(["install", "--dry-run"], repo)
    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert not (tmp_path / "install" / "claude" / "CLAUDE.md").exists()


def test_install_unknown_agent_exits_1(repo: Path) -> None:
    result = invoke(["install", "unknown"], repo)
    assert result.exit_code == 1


def test_install_is_idempotent(repo: Path) -> None:
    invoke(["install"], repo)
    result = invoke(["install"], repo)
    assert result.exit_code == 0
    assert "already linked" in result.output


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def test_remove_all_agents_unlinks(repo: Path, tmp_path: Path) -> None:
    invoke(["install"], repo)
    result = invoke(["remove"], repo)
    assert result.exit_code == 0
    assert "Done." in result.output
    assert not (tmp_path / "install" / "claude" / "CLAUDE.md").exists()
    assert not (tmp_path / "install" / "codex" / "AGENTS.md").exists()
    assert not (tmp_path / "install" / "gemini" / "GEMINI.md").exists()


def test_remove_single_agent(repo: Path, tmp_path: Path) -> None:
    invoke(["install"], repo)
    invoke(["remove", "codex"], repo)
    assert not (tmp_path / "install" / "codex" / "AGENTS.md").exists()
    assert (tmp_path / "install" / "claude" / "CLAUDE.md").is_symlink()


def test_remove_dry_run_keeps_symlinks(repo: Path, tmp_path: Path) -> None:
    invoke(["install"], repo)
    result = invoke(["remove", "--dry-run"], repo)
    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert (tmp_path / "install" / "claude" / "CLAUDE.md").is_symlink()


def test_remove_unknown_agent_exits_1(repo: Path) -> None:
    result = invoke(["remove", "unknown"], repo)
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------


def test_generate_writes_flat_file_for_codex(repo: Path) -> None:
    result = invoke(["generate"], repo)
    assert result.exit_code == 0
    assert "generated" in result.output
    assert (repo / "agents" / "codex" / "AGENTS.md").exists()


def test_generate_skips_native_import_agents(repo: Path) -> None:
    result = invoke(["generate"], repo)
    assert result.exit_code == 0
    assert "claude" not in result.output
    assert "gemini" not in result.output


def test_generate_dry_run_writes_nothing(repo: Path, tmp_path: Path) -> None:
    output = repo / "agents" / "codex" / "AGENTS.md"
    size_before = output.stat().st_size if output.exists() else None
    result = invoke(["generate", "--dry-run"], repo)
    assert result.exit_code == 0
    assert "[dry-run]" in result.output
    if size_before is not None:
        assert output.stat().st_size == size_before


def test_generate_single_agent(repo: Path) -> None:
    result = invoke(["generate", "codex"], repo)
    assert result.exit_code == 0
    assert "generated" in result.output


def test_generate_native_import_agent_outputs_no_agents_message(repo: Path) -> None:
    result = invoke(["generate", "claude"], repo)
    assert result.exit_code == 0
    assert "No agents requiring" in result.output


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------


def test_verify_exits_0_when_in_sync(repo: Path) -> None:
    invoke(["generate"], repo)
    result = invoke(["verify"], repo)
    assert result.exit_code == 0
    assert "OK" in result.output


def test_verify_exits_1_when_stale(repo: Path) -> None:
    invoke(["generate"], repo)
    (repo / "rules" / "language.md").write_text("# Updated language rule\n")
    result = invoke(["verify"], repo)
    assert result.exit_code == 1
    assert "STALE" in result.output


def test_verify_exits_1_when_flat_file_missing(repo: Path) -> None:
    flat = repo / "agents" / "codex" / "AGENTS.md"
    if flat.exists():
        flat.unlink()
    result = invoke(["verify"], repo)
    assert result.exit_code == 1
    assert "STALE" in result.output


def test_verify_skips_native_import_agents(repo: Path) -> None:
    invoke(["generate"], repo)
    result = invoke(["verify", "claude"], repo)
    assert result.exit_code == 0
    assert "No agents requiring" in result.output


def test_verify_single_agent(repo: Path) -> None:
    invoke(["generate"], repo)
    result = invoke(["verify", "codex"], repo)
    assert result.exit_code == 0
    assert "OK" in result.output


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


def test_update_installs_when_not_present(repo: Path, tmp_path: Path) -> None:
    result = invoke(["update"], repo)
    assert result.exit_code == 0
    assert (tmp_path / "install" / "claude" / "CLAUDE.md").is_symlink()


def test_update_is_idempotent(repo: Path) -> None:
    invoke(["install"], repo)
    result = invoke(["update"], repo)
    assert result.exit_code == 0
    assert "already linked" in result.output


def test_update_regenerates_flat_file_for_codex(repo: Path) -> None:
    invoke(["install"], repo)
    (repo / "rules" / "language.md").write_text("# Language\n\nUpdated rule.\n")
    result = invoke(["update", "codex"], repo)
    assert result.exit_code == 0
    assert "regenerated" in result.output
    assert "Updated rule." in (repo / "agents" / "codex" / "AGENTS.md").read_text()


def test_update_dry_run_does_not_regenerate(repo: Path) -> None:
    invoke(["generate"], repo)
    original = (repo / "agents" / "codex" / "AGENTS.md").read_text()
    (repo / "rules" / "language.md").write_text("# Language\n\nUpdated rule.\n")
    invoke(["update", "--dry-run"], repo)
    assert (repo / "agents" / "codex" / "AGENTS.md").read_text() == original


def test_update_skips_regeneration_for_native_import_agents(repo: Path) -> None:
    invoke(["install"], repo)
    result = invoke(["update", "claude"], repo)
    assert result.exit_code == 0
    assert "regenerated" not in result.output


def test_update_migrates_legacy_backups(repo: Path, tmp_path: Path) -> None:
    invoke(["install"], repo)
    legacy_dir = tmp_path / "install" / "codex" / "backup-20240101-120000"
    legacy_dir.mkdir()
    (legacy_dir / "AGENTS.md").write_text("old")
    result = invoke(["update", "codex"], repo)
    assert result.exit_code == 0
    assert "MIGRATE" in result.output
    assert not legacy_dir.exists()


# ---------------------------------------------------------------------------
# outside repo
# ---------------------------------------------------------------------------


def test_error_when_no_repo_found(tmp_path: Path) -> None:
    result = RUNNER.invoke(app, ["list"], env={"AI_RULES_HOME": str(tmp_path)})
    assert result.exit_code == 1
