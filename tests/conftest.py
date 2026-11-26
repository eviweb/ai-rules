from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def xdg_state_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect XDG_STATE_HOME to a temp dir for all tests."""
    xdg = tmp_path / "state"
    xdg.mkdir()
    monkeypatch.setenv("XDG_STATE_HOME", str(xdg))
    return xdg


@pytest.fixture(autouse=True)
def xdg_config_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect XDG_CONFIG_HOME so tests never read the user's own config."""
    xdg = tmp_path / "config"
    xdg.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    return xdg
