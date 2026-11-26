"""Freshness of the user's model tier mapping.

``ai-rules-writing-plans`` gives each task an agent-neutral tier (light,
standard, deep). The user maps tiers to models in a personal file outside the
repository, with a ``checked: YYYY-MM-DD`` line. This module only reports
whether that file exists and was checked recently; it never fails a command.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

STALE_AFTER_DAYS = 90

_CHECKED_LINE = re.compile(r"^checked:\s*(\S+)\s*$", re.MULTILINE)


def model_tiers_path() -> Path:
    """Return the tier mapping path under ``$XDG_CONFIG_HOME`` (default ``~/.config``)."""
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_home / "ai-rules" / "model-tiers.md"


def model_tiers_status(path: Path, today: date) -> tuple[bool, str]:
    """Return ``(ok, message)`` for the tier mapping at *path* as of *today*."""
    if not path.is_file():
        return False, "missing (optional): see ai-rules-writing-plans for the template"

    match = _CHECKED_LINE.search(path.read_text())
    try:
        checked = date.fromisoformat(match.group(1)) if match else None
    except ValueError:
        checked = None
    if checked is None:
        return False, "no valid 'checked: YYYY-MM-DD' line"

    if (today - checked).days >= STALE_AFTER_DAYS:
        return False, f"stale: checked {checked.isoformat()}, run /model and update the file"
    return True, f"checked {checked.isoformat()}"
