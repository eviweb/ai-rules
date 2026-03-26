from pathlib import Path

import pytest

from ai_rules.config import find_repo_root


def test_find_repo_root_via_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "agents.toml").touch()
    monkeypatch.setenv("AI_RULES_HOME", str(tmp_path))
    assert find_repo_root() == tmp_path


def test_find_repo_root_env_missing_agents_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AI_RULES_HOME", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="AI_RULES_HOME"):
        find_repo_root()


def test_find_repo_root_walks_up_from_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "agents.toml").touch()
    subdir = tmp_path / "sub" / "dir"
    subdir.mkdir(parents=True)
    monkeypatch.chdir(subdir)
    monkeypatch.delenv("AI_RULES_HOME", raising=False)
    assert find_repo_root() == tmp_path


def test_find_repo_root_finds_in_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "agents.toml").touch()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AI_RULES_HOME", raising=False)
    assert find_repo_root() == tmp_path


def test_find_repo_root_raises_when_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AI_RULES_HOME", raising=False)
    with pytest.raises(FileNotFoundError, match="agents.toml"):
        find_repo_root()
