from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.agent import Agent, ConfigPatch, Link
from ai_rules.installer import (
    _patch_toml_file,
    _xdg_backup_dir,
    install_agent,
    migrate_agent_backups,
    remove_agent,
    status_agent,
)


def make_agent(install_dir: Path, links: list[tuple[str, str]]) -> Agent:
    return Agent(
        key="test",
        name="Test Agent",
        entry_point="entry.md",
        install_dir=str(install_dir),
        supports_imports=True,
        condense_flat_file=False,
        links=[Link(source=src, target=tgt) for src, tgt in links],
    )


def make_patch_agent(
    install_dir: Path,
    patches: list[tuple[str, str, object]],
) -> Agent:
    return Agent(
        key="test",
        name="Test Agent",
        entry_point="entry.md",
        install_dir=str(install_dir),
        supports_imports=False,
        condense_flat_file=False,
        links=[],
        config_patches=[
            ConfigPatch(file=f, key=k, value=v) for f, k, v in patches
        ],
    )


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    source = tmp_path / "repo"
    source.mkdir()
    (source / "entry.md").write_text("# Entry")
    (source / "rules").mkdir()
    return source


@pytest.fixture()
def install_dir(tmp_path: Path) -> Path:
    target = tmp_path / "install"
    target.mkdir()
    return target


def test_install_agent_creates_symlink(repo_root: Path, install_dir: Path) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    link = install_dir / "entry.md"
    assert link.is_symlink()
    assert link.resolve() == (repo_root / "entry.md").resolve()


def test_install_agent_skips_correct_existing_symlink(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    actions = install_agent(repo_root, agent)
    assert any("already linked" in a for a in actions)


def test_install_agent_backs_up_existing_file(
    repo_root: Path, install_dir: Path
) -> None:
    existing = install_dir / "entry.md"
    existing.write_text("old content")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    actions = install_agent(repo_root, agent)
    assert any("BACKUP" in a for a in actions)
    assert (install_dir / "entry.md").is_symlink()
    backup_root = _xdg_backup_dir("test")
    backups = list(backup_root.glob("backup-*/entry.md"))
    assert len(backups) == 1
    assert backups[0].read_text() == "old content"


def test_install_agent_dry_run_makes_no_changes(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent, dry_run=True)
    assert not (install_dir / "entry.md").exists()


def test_install_agent_skips_missing_source(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_agent(install_dir, [("missing.md", "missing.md")])
    actions = install_agent(repo_root, agent)
    assert any("SKIP" in a for a in actions)
    assert not (install_dir / "missing.md").exists()


def test_status_agent_ok(repo_root: Path, install_dir: Path) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    results = status_agent(repo_root, agent)
    assert results == [("entry.md", "ok")]


def test_status_agent_not_installed(repo_root: Path, install_dir: Path) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    results = status_agent(repo_root, agent)
    assert results == [("entry.md", "not installed")]


def test_status_agent_symlink_mismatch(repo_root: Path, install_dir: Path) -> None:
    other = install_dir / "other.md"
    other.write_text("other")
    link = install_dir / "entry.md"
    link.symlink_to(other)
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    results = status_agent(repo_root, agent)
    assert "symlink mismatch" in results[0][1]


def test_status_agent_exists_not_symlink(repo_root: Path, install_dir: Path) -> None:
    (install_dir / "entry.md").write_text("manual")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    results = status_agent(repo_root, agent)
    assert results == [("entry.md", "exists (not a symlink)")]


# --- config_patches ---


def test_patch_toml_creates_file_with_key(install_dir: Path) -> None:
    target = install_dir / "config.toml"
    patch = ConfigPatch(file="config.toml", key="max_bytes", value=65536)
    _patch_toml_file(target, patch, "test")
    assert "max_bytes = 65536" in target.read_text()


def test_patch_toml_updates_existing_key(install_dir: Path) -> None:
    target = install_dir / "config.toml"
    target.write_text("max_bytes = 1024\n")
    patch = ConfigPatch(file="config.toml", key="max_bytes", value=65536)
    _patch_toml_file(target, patch, "test")
    assert "max_bytes = 65536" in target.read_text()
    assert "1024" not in target.read_text()


def test_patch_toml_backs_up_before_modifying(install_dir: Path) -> None:
    target = install_dir / "config.toml"
    target.write_text("max_bytes = 1024\n")
    patch = ConfigPatch(file="config.toml", key="max_bytes", value=65536)
    _patch_toml_file(target, patch, "test")
    backup_root = _xdg_backup_dir("test")
    backups = list(backup_root.glob("*.bak"))
    assert len(backups) == 1
    assert "1024" in backups[0].read_text()


def test_patch_toml_skips_when_already_correct(install_dir: Path) -> None:
    target = install_dir / "config.toml"
    target.write_text("max_bytes = 65536\n")
    patch = ConfigPatch(file="config.toml", key="max_bytes", value=65536)
    actions = _patch_toml_file(target, patch, "test")
    assert any("already set" in a for a in actions)
    assert not list(_xdg_backup_dir("test").glob("*.bak"))


def test_patch_toml_preserves_existing_sections(install_dir: Path) -> None:
    target = install_dir / "config.toml"
    target.write_text('max_bytes = 1024\n\n[projects."foo"]\ntrust = "trusted"\n')
    patch = ConfigPatch(file="config.toml", key="max_bytes", value=65536)
    _patch_toml_file(target, patch, "test")
    content = target.read_text()
    assert "max_bytes = 65536" in content
    assert 'trust = "trusted"' in content


def test_patch_toml_dry_run_makes_no_changes(install_dir: Path) -> None:
    target = install_dir / "config.toml"
    target.write_text("max_bytes = 1024\n")
    patch = ConfigPatch(file="config.toml", key="max_bytes", value=65536)
    _patch_toml_file(target, patch, "test", dry_run=True)
    assert "1024" in target.read_text()
    assert not list(_xdg_backup_dir("test").glob("*.bak"))


def test_install_agent_applies_config_patches(repo_root: Path, install_dir: Path) -> None:
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    actions = install_agent(repo_root, agent)
    assert any("PATCH" in a for a in actions)
    assert "max_bytes = 65536" in (install_dir / "config.toml").read_text()


def test_status_agent_config_patch_ok(repo_root: Path, install_dir: Path) -> None:
    (install_dir / "config.toml").write_text("max_bytes = 65536\n")
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    results = status_agent(repo_root, agent)
    assert results == [("config.toml", "ok")]


def test_status_agent_config_patch_not_installed(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    results = status_agent(repo_root, agent)
    assert results == [("config.toml", "not installed")]


def test_status_agent_config_patch_needs_update(
    repo_root: Path, install_dir: Path
) -> None:
    (install_dir / "config.toml").write_text("max_bytes = 1024\n")
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    results = status_agent(repo_root, agent)
    assert results[0][1].startswith("patch needed")


# --- remove_agent ---


def test_remove_agent_unlinks_symlink(repo_root: Path, install_dir: Path) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent)
    assert not (install_dir / "entry.md").exists()


def test_remove_agent_restores_backup(repo_root: Path, install_dir: Path) -> None:
    original = install_dir / "entry.md"
    original.write_text("original content")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent)
    assert original.exists()
    assert not original.is_symlink()
    assert original.read_text() == "original content"


def test_remove_agent_cleans_empty_backup_dir(repo_root: Path, install_dir: Path) -> None:
    (install_dir / "entry.md").write_text("original")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent)
    backup_root = _xdg_backup_dir("test")
    assert not any(backup_root.glob("backup-*"))


def test_remove_agent_skips_unmanaged_symlink(repo_root: Path, install_dir: Path) -> None:
    other = install_dir / "other.md"
    other.write_text("other")
    link = install_dir / "entry.md"
    link.symlink_to(other)
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    actions = remove_agent(repo_root, agent)
    assert any("SKIP" in a for a in actions)
    assert link.exists()


def test_remove_agent_dry_run_makes_no_changes(repo_root: Path, install_dir: Path) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent, dry_run=True)
    assert (install_dir / "entry.md").is_symlink()


def test_remove_agent_restores_toml_backup(repo_root: Path, install_dir: Path) -> None:
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    (install_dir / "config.toml").write_text("max_bytes = 1024\n")
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent)
    assert "max_bytes = 1024" in (install_dir / "config.toml").read_text()
    assert not list(_xdg_backup_dir("test").glob("*.bak"))


def test_remove_agent_unpatches_toml_when_no_backup(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent)
    content = (install_dir / "config.toml").read_text()
    assert "max_bytes" not in content


def test_remove_agent_toml_dry_run_makes_no_changes(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    install_agent(repo_root, agent)
    remove_agent(repo_root, agent, dry_run=True)
    assert "max_bytes = 65536" in (install_dir / "config.toml").read_text()


# --- migrate_agent_backups ---


def test_migrate_agent_backups_moves_legacy_link_backup(
    install_dir: Path,
) -> None:
    legacy_dir = install_dir / "backup-20240101-120000"
    legacy_dir.mkdir()
    (legacy_dir / "entry.md").write_text("old")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    actions = migrate_agent_backups(agent)
    assert any("MIGRATE" in a for a in actions)
    assert not legacy_dir.exists()
    xdg_dir = _xdg_backup_dir("test")
    assert (xdg_dir / "backup-20240101-120000" / "entry.md").read_text() == "old"


def test_migrate_agent_backups_moves_legacy_toml_bak(
    install_dir: Path,
) -> None:
    bak = install_dir / "config.toml.20240101-120000.bak"
    bak.write_text("max_bytes = 1024\n")
    agent = make_patch_agent(install_dir, [("config.toml", "max_bytes", 65536)])
    actions = migrate_agent_backups(agent)
    assert any("MIGRATE" in a for a in actions)
    assert not bak.exists()
    xdg_dir = _xdg_backup_dir("test")
    assert (xdg_dir / bak.name).read_text() == "max_bytes = 1024\n"


def test_migrate_agent_backups_no_legacy_no_actions(install_dir: Path) -> None:
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    actions = migrate_agent_backups(agent)
    assert actions == []


def test_migrate_agent_backups_dry_run_makes_no_changes(install_dir: Path) -> None:
    legacy_dir = install_dir / "backup-20240101-120000"
    legacy_dir.mkdir()
    (legacy_dir / "entry.md").write_text("old")
    agent = make_agent(install_dir, [("entry.md", "entry.md")])
    actions = migrate_agent_backups(agent, dry_run=True)
    assert any("MIGRATE" in a for a in actions)
    assert legacy_dir.exists()
    assert not _xdg_backup_dir("test").exists()
