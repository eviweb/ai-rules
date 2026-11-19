from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_rules.agent import Agent, SettingsMerge, load_agents
from ai_rules.installer import install_agent, remove_agent, status_agent
from ai_rules.settings_merge import (
    LEGACY_ALLOW,
    LEGACY_DENY,
    merge_settings,
    status_settings,
    unmerge_settings,
)

FRAGMENT = {
    "permissions": {
        "allow": ["Read", "Bash(ls)"],
        "deny": ["Bash(sudo *)"],
    },
    "autoApprove": False,
}
OWNED = ["permissions.allow", "permissions.deny", "permissions.ask", "autoApprove"]


def make_agent(install_dir: Path, owned: list[str] | None = None) -> Agent:
    return Agent(
        key="claude",
        name="Test Claude",
        entry_point="entry.md",
        install_dir=str(install_dir),
        supports_imports=True,
        condense_flat_file=False,
        links=[],
        settings_merges=[
            SettingsMerge(
                file="settings.json",
                source="settings.json",
                owned=owned if owned is not None else OWNED,
            )
        ],
    )


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    write_json(root / "settings.json", FRAGMENT)
    return root


@pytest.fixture()
def install_dir(tmp_path: Path) -> Path:
    target = tmp_path / "install"
    target.mkdir()
    return target


@pytest.fixture()
def agent(install_dir: Path) -> Agent:
    return make_agent(install_dir)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def state_file(xdg_state_home: Path) -> Path:
    return xdg_state_home / "ai-rules" / "state" / "claude-settings.json"


def merge(repo_root: Path, agent: Agent, dry_run: bool = False) -> list[str]:
    return merge_settings(repo_root, agent, agent.settings_merges[0], dry_run=dry_run)


def unmerge(repo_root: Path, agent: Agent, dry_run: bool = False) -> list[str]:
    return unmerge_settings(repo_root, agent, agent.settings_merges[0], dry_run=dry_run)


# --- merge ---


def test_merge_creates_file_when_absent(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    merge(repo_root, agent)

    assert read_json(install_dir / "settings.json") == FRAGMENT


def test_merge_preserves_foreign_keys_and_user_entries(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    write_json(
        install_dir / "settings.json",
        {"tui": "fullscreen", "permissions": {"allow": ["Bash(make *)"]}},
    )

    merge(repo_root, agent)

    data = read_json(install_dir / "settings.json")
    assert data["tui"] == "fullscreen"
    assert data["permissions"]["allow"] == ["Bash(make *)", "Read", "Bash(ls)"]


def test_merge_is_idempotent(repo_root: Path, agent: Agent, install_dir: Path) -> None:
    merge(repo_root, agent)
    first = (install_dir / "settings.json").read_text()

    actions = merge(repo_root, agent)

    assert (install_dir / "settings.json").read_text() == first
    assert any(a.startswith("OK") for a in actions)


def test_merge_dry_run_writes_nothing(
    repo_root: Path, agent: Agent, install_dir: Path, xdg_state_home: Path
) -> None:
    actions = merge(repo_root, agent, dry_run=True)

    assert not (install_dir / "settings.json").exists()
    assert not state_file(xdg_state_home).exists()
    assert any(a.startswith("MERGE") for a in actions)


def test_merge_skips_invalid_json_without_touching_file(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    (install_dir / "settings.json").write_text("{not json")

    actions = merge(repo_root, agent)

    assert (install_dir / "settings.json").read_text() == "{not json"
    assert any("parse error" in a for a in actions)


def test_merge_backs_up_existing_file_before_modifying(
    repo_root: Path, agent: Agent, install_dir: Path, xdg_state_home: Path
) -> None:
    write_json(install_dir / "settings.json", {"tui": "fullscreen"})

    merge(repo_root, agent)

    backups = list((xdg_state_home / "ai-rules" / "backups" / "claude").glob("settings.json.*.bak"))
    assert len(backups) == 1
    assert read_json(backups[0]) == {"tui": "fullscreen"}


def test_merge_ignores_fragment_keys_that_are_not_owned(
    repo_root: Path, install_dir: Path
) -> None:
    agent = make_agent(install_dir, owned=["permissions.deny"])

    merge(repo_root, agent)

    assert read_json(install_dir / "settings.json") == {"permissions": {"deny": ["Bash(sudo *)"]}}


def test_merge_removes_entries_dropped_from_fragment(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    merge(repo_root, agent)
    data = read_json(install_dir / "settings.json")
    data["permissions"]["allow"].append("Bash(make *)")
    write_json(install_dir / "settings.json", data)
    write_json(
        repo_root / "settings.json",
        {"permissions": {"allow": ["Read"], "deny": ["Bash(sudo *)"]}, "autoApprove": False},
    )

    merge(repo_root, agent)

    allow = read_json(install_dir / "settings.json")["permissions"]["allow"]
    assert allow == ["Read", "Bash(make *)"]


def test_merge_removes_scalar_dropped_from_fragment(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    merge(repo_root, agent)
    write_json(repo_root / "settings.json", {"permissions": FRAGMENT["permissions"]})

    merge(repo_root, agent)

    assert "autoApprove" not in read_json(install_dir / "settings.json")


# --- unmerge ---


def test_unmerge_removes_only_entries_added_by_ai_rules(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    write_json(
        install_dir / "settings.json",
        {"tui": "fullscreen", "permissions": {"allow": ["Bash(make *)"]}},
    )
    merge(repo_root, agent)

    unmerge(repo_root, agent)

    assert read_json(install_dir / "settings.json") == {
        "tui": "fullscreen",
        "permissions": {"allow": ["Bash(make *)"]},
    }


def test_unmerge_keeps_entries_that_existed_before_install(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    write_json(install_dir / "settings.json", {"permissions": {"allow": ["Read"]}})
    merge(repo_root, agent)

    unmerge(repo_root, agent)

    assert read_json(install_dir / "settings.json") == {"permissions": {"allow": ["Read"]}}


def test_unmerge_deletes_file_created_by_ai_rules_when_empty(
    repo_root: Path, agent: Agent, install_dir: Path, xdg_state_home: Path
) -> None:
    merge(repo_root, agent)

    unmerge(repo_root, agent)

    assert not (install_dir / "settings.json").exists()
    assert not state_file(xdg_state_home).exists()


def test_unmerge_restores_previous_scalar_value(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    write_json(install_dir / "settings.json", {"autoApprove": True})
    merge(repo_root, agent)
    assert read_json(install_dir / "settings.json")["autoApprove"] is False

    unmerge(repo_root, agent)

    assert read_json(install_dir / "settings.json") == {"autoApprove": True}


def test_unmerge_dry_run_makes_no_changes(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    merge(repo_root, agent)
    before = (install_dir / "settings.json").read_text()

    actions = unmerge(repo_root, agent, dry_run=True)

    assert (install_dir / "settings.json").read_text() == before
    assert any(a.startswith("UNMERGE") for a in actions)


def test_unmerge_without_state_is_a_no_op(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    write_json(install_dir / "settings.json", {"permissions": {"allow": ["Read"]}})

    actions = unmerge(repo_root, agent)

    assert read_json(install_dir / "settings.json") == {"permissions": {"allow": ["Read"]}}
    assert any(a.startswith("SKIP") for a in actions)


# --- legacy symlink migration ---


def test_merge_migrates_legacy_symlink_to_regular_file(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    # Legacy install: ~/.claude/settings.json symlinked to the repo file, which
    # Claude Code also wrote into.
    write_json(repo_root / "settings.json", {**FRAGMENT, "tui": "fullscreen"})
    (install_dir / "settings.json").symlink_to(repo_root / "settings.json")

    actions = merge(repo_root, agent)

    target = install_dir / "settings.json"
    assert not target.is_symlink()
    assert read_json(target)["tui"] == "fullscreen"
    assert any(a.startswith("MIGRATE") for a in actions)


def test_merge_after_migration_leaves_repo_file_untouched(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    (install_dir / "settings.json").symlink_to(repo_root / "settings.json")
    before = (repo_root / "settings.json").read_text()

    merge(repo_root, agent)
    data = read_json(install_dir / "settings.json")
    data["tui"] = "fullscreen"
    write_json(install_dir / "settings.json", data)

    assert (repo_root / "settings.json").read_text() == before


def test_migration_treats_legacy_entries_as_owned(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    legacy = {
        "permissions": {"allow": [*LEGACY_ALLOW, "Bash(make *)"], "deny": list(LEGACY_DENY)},
        "autoApprove": False,
    }
    write_json(repo_root / "settings.json", legacy)
    (install_dir / "settings.json").symlink_to(repo_root / "settings.json")
    # New fragment no longer carries the legacy allow list.
    new_repo = repo_root.parent / "repo-new"
    new_repo.mkdir()
    write_json(new_repo / "settings.json", FRAGMENT)

    merge_settings(
        new_repo,
        agent,
        agent.settings_merges[0],
    )

    allow = read_json(install_dir / "settings.json")["permissions"]["allow"]
    assert allow == ["Read", "Bash(ls)", "Bash(make *)"]


def test_merge_replaces_broken_legacy_symlink(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    (install_dir / "settings.json").symlink_to(repo_root / "gone.json")

    merge(repo_root, agent)

    target = install_dir / "settings.json"
    assert not target.is_symlink()
    assert read_json(target) == FRAGMENT


def test_unmerge_removes_legacy_symlink_still_in_place(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    (install_dir / "settings.json").symlink_to(repo_root / "settings.json")

    actions = unmerge(repo_root, agent)

    assert not (install_dir / "settings.json").exists()
    assert any(a.startswith("UNLINK") for a in actions)


# --- status ---


def test_status_not_installed(repo_root: Path, agent: Agent) -> None:
    assert status_settings(repo_root, agent, agent.settings_merges[0]) == "not installed"


def test_status_ok_after_merge(repo_root: Path, agent: Agent) -> None:
    merge(repo_root, agent)

    assert status_settings(repo_root, agent, agent.settings_merges[0]) == "ok"


def test_status_reports_missing_entries(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    write_json(install_dir / "settings.json", {"permissions": {"allow": ["Read"]}})

    state = status_settings(repo_root, agent, agent.settings_merges[0])

    assert state.startswith("patch needed")


def test_status_flags_legacy_symlink(repo_root: Path, agent: Agent, install_dir: Path) -> None:
    (install_dir / "settings.json").symlink_to(repo_root / "settings.json")

    state = status_settings(repo_root, agent, agent.settings_merges[0])

    assert "legacy symlink" in state


# --- wiring: agents.toml, install / remove / status ---


def test_load_agents_parses_settings_merge(tmp_path: Path) -> None:
    config = tmp_path / "agents.toml"
    config.write_text(
        """
[agents.claude]
name = "Claude Code"
entry_point = "agents/claude/CLAUDE.md"
install_dir = "~/.claude"

  [[agents.claude.settings_merge]]
  file = "settings.json"
  source = "settings.json"
  owned = ["permissions.allow", "permissions.deny"]
"""
    )

    merges = load_agents(config)["claude"].settings_merges

    assert merges == [
        SettingsMerge(
            file="settings.json",
            source="settings.json",
            owned=["permissions.allow", "permissions.deny"],
        )
    ]


def test_install_and_remove_agent_apply_settings_merge(
    repo_root: Path, agent: Agent, install_dir: Path
) -> None:
    actions = install_agent(repo_root, agent)
    assert read_json(install_dir / "settings.json") == FRAGMENT
    assert any("settings.json" in a for a in actions)

    remove_agent(repo_root, agent)

    assert not (install_dir / "settings.json").exists()


def test_status_agent_reports_settings_merge(repo_root: Path, agent: Agent) -> None:
    assert ("settings.json", "not installed") in status_agent(repo_root, agent)

    install_agent(repo_root, agent)

    assert ("settings.json", "ok") in status_agent(repo_root, agent)
