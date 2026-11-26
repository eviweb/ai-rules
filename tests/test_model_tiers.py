from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ai_rules.model_tiers import STALE_AFTER_DAYS, model_tiers_path, model_tiers_status

TODAY = date(2026, 11, 26)


def _tiers_file(tmp_path: Path, checked_line: str) -> Path:
    path = tmp_path / "model-tiers.md"
    path.write_text(f"light: small, effort low\nstandard: mid, effort medium\ndeep: big, effort high\n{checked_line}\n")
    return path


def test_path_follows_xdg_config_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert model_tiers_path() == tmp_path / "ai-rules" / "model-tiers.md"


def test_path_defaults_to_dot_config_without_xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert model_tiers_path() == tmp_path / ".config" / "ai-rules" / "model-tiers.md"


def test_recent_check_is_ok(tmp_path: Path) -> None:
    path = _tiers_file(tmp_path, "checked: 2026-11-26")

    assert model_tiers_status(path, TODAY) == (True, "checked 2026-11-26")


def test_check_one_day_before_the_threshold_is_ok(tmp_path: Path) -> None:
    path = _tiers_file(tmp_path, "checked: 2026-08-29")

    assert (TODAY - date(2026, 8, 29)).days == STALE_AFTER_DAYS - 1
    assert model_tiers_status(path, TODAY)[0] is True


def test_check_at_the_threshold_is_stale(tmp_path: Path) -> None:
    path = _tiers_file(tmp_path, "checked: 2026-08-28")

    ok, message = model_tiers_status(path, TODAY)

    assert ok is False
    assert message == "stale: checked 2026-08-28, run /model and update the file"


def test_missing_file_is_reported_as_optional(tmp_path: Path) -> None:
    ok, message = model_tiers_status(tmp_path / "absent.md", TODAY)

    assert ok is False
    assert message == "missing (optional): see ai-rules-writing-plans for the template"


@pytest.mark.parametrize("checked_line", ["", "checked: yesterday", "checked: 2026-13-40"])
def test_missing_or_invalid_checked_line_is_reported(tmp_path: Path, checked_line: str) -> None:
    path = _tiers_file(tmp_path, checked_line)

    assert model_tiers_status(path, TODAY) == (False, "no valid 'checked: YYYY-MM-DD' line")


def test_stale_threshold_is_three_months() -> None:
    assert STALE_AFTER_DAYS == 90
