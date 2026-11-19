from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def permissions() -> dict[str, list[str]]:
    data = json.loads((REPO_ROOT / "settings.json").read_text())
    return data["permissions"]


def test_fragment_has_no_undocumented_auto_approve_key() -> None:
    data = json.loads((REPO_ROOT / "settings.json").read_text())

    assert "autoApprove" not in data


@pytest.mark.parametrize(
    "rule",
    ["Bash(git commit *)", "Bash(git push *)", "Bash(rm *)", "Bash(npx *)", "Bash(chmod *)"],
)
def test_fragment_asks_before_risky_commands(
    permissions: dict[str, list[str]], rule: str
) -> None:
    assert rule in permissions["ask"]


@pytest.mark.parametrize(
    "rule",
    [
        "Bash(rm -rf *)",
        "Bash(rm -fr *)",
        "Bash(rm -r *)",
        "Bash(rm -R *)",
        "Bash(git push --force *)",
        "Bash(git push -f *)",
        "Bash(git reset --hard *)",
        "Bash(git checkout -- *)",
        "Bash(git clean *)",
        "Bash(git branch -D *)",
        "Bash(sudo *)",
    ],
)
def test_fragment_denies_destructive_commands(
    permissions: dict[str, list[str]], rule: str
) -> None:
    assert rule in permissions["deny"]


def test_fragment_does_not_deny_force_with_lease(permissions: dict[str, list[str]]) -> None:
    # git.md allows --force-with-lease on personal branches: it stays under `ask`.
    assert not any("force-with-lease" in rule for rule in permissions["deny"])
    assert not any(rule.startswith("Bash(git push --force*") for rule in permissions["deny"])


def test_fragment_has_no_rule_in_several_lists(permissions: dict[str, list[str]]) -> None:
    allow, ask, deny = (set(permissions[key]) for key in ("allow", "ask", "deny"))

    assert not allow & ask
    assert not allow & deny
    assert not ask & deny


def test_fragment_has_no_duplicate_rules(permissions: dict[str, list[str]]) -> None:
    for key in ("allow", "ask", "deny"):
        assert len(permissions[key]) == len(set(permissions[key])), key


def test_agents_toml_owns_every_permission_list() -> None:
    agents = tomllib.loads((REPO_ROOT / "agents.toml").read_text())
    owned = agents["agents"]["claude"]["settings_merge"][0]["owned"]

    for key in ("permissions.allow", "permissions.ask", "permissions.deny"):
        assert key in owned
    assert "autoApprove" not in owned
