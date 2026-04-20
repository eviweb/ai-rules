from pathlib import Path

import pytest

from ai_rules.agent import Agent, Link
from ai_rules.installer import install_agent, status_agent


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
