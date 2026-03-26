from __future__ import annotations

import os
from pathlib import Path

AGENTS_FILENAME = "agents.toml"


def find_repo_root() -> Path:
    """Locate the ai-rules repository root.

    Resolution order:
    1. AI_RULES_HOME environment variable
    2. Walk up from current working directory looking for agents.toml
    """
    env_home = os.environ.get("AI_RULES_HOME")
    if env_home:
        path = Path(env_home).expanduser().resolve()
        if not (path / AGENTS_FILENAME).exists():
            raise FileNotFoundError(
                f"AI_RULES_HOME is set to '{path}' but no {AGENTS_FILENAME} was found there."
            )
        return path

    for directory in [Path.cwd(), *Path.cwd().parents]:
        if (directory / AGENTS_FILENAME).exists():
            return directory

    raise FileNotFoundError(
        f"Could not find {AGENTS_FILENAME}. "
        "Run from the ai-rules repository or set the AI_RULES_HOME environment variable."
    )
