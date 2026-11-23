from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.agent import Agent, SkillDir, load_agents
from ai_rules.installer import (
    _xdg_backup_dir,
    install_agent,
    remove_agent,
    status_agent,
)


def make_skill(repo_root: Path, name: str) -> Path:
    skill = repo_root / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n# {name}\n")
    return skill


def make_skills_agent(install_dir: Path) -> Agent:
    return Agent(
        key="test",
        name="Test Agent",
        entry_point="entry.md",
        install_dir=str(install_dir),
        supports_imports=True,
        condense_flat_file=False,
        links=[],
        skill_dirs=[SkillDir(source="skills", target="skills")],
    )


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


@pytest.fixture()
def install_dir(tmp_path: Path) -> Path:
    target = tmp_path / "install"
    target.mkdir()
    return target


# --- loading ---------------------------------------------------------------


def test_load_agents_parses_skill_dirs(tmp_path: Path) -> None:
    config = tmp_path / "agents.toml"
    config.write_text(
        """
[agents.claude]
name = "Claude Code"
entry_point = "agents/claude/CLAUDE.md"
install_dir = "~/.claude"

  [[agents.claude.skill_dirs]]
  source = "skills"
  target = "skills"
"""
    )
    agent = load_agents(config)["claude"]
    assert agent.skill_dirs == [SkillDir(source="skills", target="skills")]


def test_load_agents_defaults_skill_dirs_to_empty(tmp_path: Path) -> None:
    config = tmp_path / "agents.toml"
    config.write_text(
        '[agents.x]\nname = "X"\nentry_point = "e"\ninstall_dir = "~/.x"\n'
    )
    assert load_agents(config)["x"].skill_dirs == []


# --- install ---------------------------------------------------------------


def test_install_links_each_skill_folder(repo_root: Path, install_dir: Path) -> None:
    source_a = make_skill(repo_root, "ai-rules-a")
    source_b = make_skill(repo_root, "ai-rules-b")
    agent = make_skills_agent(install_dir)

    actions = install_agent(repo_root, agent)

    assert (install_dir / "skills" / "ai-rules-a").resolve() == source_a.resolve()
    assert (install_dir / "skills" / "ai-rules-b").resolve() == source_b.resolve()
    assert (install_dir / "skills" / "ai-rules-a").is_symlink()
    assert any("LINK" in a and "skills/ai-rules-a" in a for a in actions)


def test_install_skips_folders_without_skill_md(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    (repo_root / "skills" / "drafts").mkdir()
    (repo_root / "skills" / "README.md").write_text("index")

    install_agent(repo_root, make_skills_agent(install_dir))

    assert sorted(p.name for p in (install_dir / "skills").iterdir()) == ["ai-rules-a"]


def test_install_keeps_user_skills_untouched(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    mine = install_dir / "skills" / "my-skill"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text("mine")

    install_agent(repo_root, make_skills_agent(install_dir))

    assert not mine.is_symlink()
    assert (mine / "SKILL.md").read_text() == "mine"


def test_install_is_idempotent(repo_root: Path, install_dir: Path) -> None:
    make_skill(repo_root, "ai-rules-a")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)

    actions = install_agent(repo_root, agent)

    assert any("OK" in a and "already linked" in a for a in actions)
    assert not any(a.startswith(("LINK", "UPDATE", "BACKUP")) for a in actions)


def test_install_backs_up_existing_folder_with_same_name(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    existing = install_dir / "skills" / "ai-rules-a"
    existing.mkdir(parents=True)
    (existing / "SKILL.md").write_text("old")

    actions = install_agent(repo_root, make_skills_agent(install_dir))

    assert any("BACKUP" in a for a in actions)
    assert existing.is_symlink()
    backups = list(_xdg_backup_dir("test").glob("backup-*/ai-rules-a/SKILL.md"))
    assert [b.read_text() for b in backups] == ["old"]


def test_install_relinks_symlink_pointing_elsewhere(
    repo_root: Path, install_dir: Path, tmp_path: Path
) -> None:
    source = make_skill(repo_root, "ai-rules-a")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (install_dir / "skills").mkdir()
    (install_dir / "skills" / "ai-rules-a").symlink_to(elsewhere)

    actions = install_agent(repo_root, make_skills_agent(install_dir))

    assert any("UPDATE" in a for a in actions)
    assert (install_dir / "skills" / "ai-rules-a").resolve() == source.resolve()


def test_install_removes_links_of_skills_deleted_from_repository(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    gone = make_skill(repo_root, "ai-rules-gone")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)
    (gone / "SKILL.md").unlink()
    gone.rmdir()

    actions = install_agent(repo_root, agent)

    assert not (install_dir / "skills" / "ai-rules-gone").is_symlink()
    assert (install_dir / "skills" / "ai-rules-a").is_symlink()
    assert any("UNLINK" in a and "ai-rules-gone" in a for a in actions)


def test_install_never_prunes_foreign_symlinks(
    repo_root: Path, install_dir: Path, tmp_path: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    foreign = tmp_path / "foreign-skill"
    foreign.mkdir()
    (install_dir / "skills").mkdir()
    (install_dir / "skills" / "foreign").symlink_to(foreign)

    install_agent(repo_root, make_skills_agent(install_dir))

    assert (install_dir / "skills" / "foreign").is_symlink()


def test_install_dry_run_changes_nothing(repo_root: Path, install_dir: Path) -> None:
    make_skill(repo_root, "ai-rules-a")

    actions = install_agent(repo_root, make_skills_agent(install_dir), dry_run=True)

    assert any("LINK" in a for a in actions)
    assert not (install_dir / "skills").exists()


def test_install_missing_source_directory_is_skipped(
    repo_root: Path, install_dir: Path
) -> None:
    actions = install_agent(repo_root, make_skills_agent(install_dir))

    assert any("SKIP" in a and "source not found" in a for a in actions)
    assert not (install_dir / "skills").exists()


def test_install_refuses_when_target_is_a_symlink_to_the_source(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    (install_dir / "skills").symlink_to(repo_root / "skills")

    actions = install_agent(repo_root, make_skills_agent(install_dir))

    assert any("SKIP" in a and "symlink" in a for a in actions)
    assert not (repo_root / "skills" / "ai-rules-a").is_symlink()


# --- remove ----------------------------------------------------------------


def test_remove_unlinks_only_ai_rules_skills(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)
    mine = install_dir / "skills" / "my-skill"
    mine.mkdir()

    actions = remove_agent(repo_root, agent)

    assert not (install_dir / "skills" / "ai-rules-a").exists()
    assert mine.is_dir()
    assert any("UNLINK" in a and "ai-rules-a" in a for a in actions)


def test_remove_restores_backed_up_folder(repo_root: Path, install_dir: Path) -> None:
    make_skill(repo_root, "ai-rules-a")
    existing = install_dir / "skills" / "ai-rules-a"
    existing.mkdir(parents=True)
    (existing / "SKILL.md").write_text("old")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)

    remove_agent(repo_root, agent)

    assert not existing.is_symlink()
    assert (existing / "SKILL.md").read_text() == "old"


def test_remove_also_unlinks_stale_skills(repo_root: Path, install_dir: Path) -> None:
    gone = make_skill(repo_root, "ai-rules-gone")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)
    (gone / "SKILL.md").unlink()
    gone.rmdir()

    remove_agent(repo_root, agent)

    assert not (install_dir / "skills" / "ai-rules-gone").is_symlink()


def test_remove_dry_run_changes_nothing(repo_root: Path, install_dir: Path) -> None:
    make_skill(repo_root, "ai-rules-a")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)

    remove_agent(repo_root, agent, dry_run=True)

    assert (install_dir / "skills" / "ai-rules-a").is_symlink()


# --- status ----------------------------------------------------------------


def test_status_reports_ok_and_not_installed(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    make_skill(repo_root, "ai-rules-b")
    agent = make_skills_agent(install_dir)
    (install_dir / "skills").mkdir()
    (install_dir / "skills" / "ai-rules-a").symlink_to(
        repo_root / "skills" / "ai-rules-a"
    )

    states = dict(status_agent(repo_root, agent))

    assert states["skills/ai-rules-a"] == "ok"
    assert states["skills/ai-rules-b"] == "not installed"


def test_status_reports_real_folder_in_the_way(
    repo_root: Path, install_dir: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    (install_dir / "skills" / "ai-rules-a").mkdir(parents=True)

    states = dict(status_agent(repo_root, make_skills_agent(install_dir)))

    assert states["skills/ai-rules-a"] == "exists (not a symlink)"


def test_status_reports_symlink_mismatch(
    repo_root: Path, install_dir: Path, tmp_path: Path
) -> None:
    make_skill(repo_root, "ai-rules-a")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (install_dir / "skills").mkdir()
    (install_dir / "skills" / "ai-rules-a").symlink_to(elsewhere)

    states = dict(status_agent(repo_root, make_skills_agent(install_dir)))

    assert states["skills/ai-rules-a"].startswith("symlink mismatch")


def test_status_reports_stale_skill(repo_root: Path, install_dir: Path) -> None:
    gone = make_skill(repo_root, "ai-rules-gone")
    agent = make_skills_agent(install_dir)
    install_agent(repo_root, agent)
    (gone / "SKILL.md").unlink()
    gone.rmdir()

    states = dict(status_agent(repo_root, agent))

    assert states["skills/ai-rules-gone"].startswith("stale")
