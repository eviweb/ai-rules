"""Normative invariants: rules that must stay reachable wherever they are hosted.

R3 moves rule text between ``rules/``, ``core/`` and ``skills/``. These tests
check that each cross-cutting behaviour still exists somewhere in the shipped
instruction corpus, so condensing or relocating a file cannot silently drop it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIRS = ("core", "rules", "skills")

# (phrase, why it matters). Matching is case-insensitive.
INVARIANTS = [
    ("never commit autonomously", "no autonomous commits"),
    ("wait for the user's explicit go-ahead", "commit gate"),
    ("git commit -s", "signed-off commits"),
    ("no attribution", "no attribution lines"),
    ("propose before implementing", "design validation before code"),
    ("propose options before deciding", "options before structuring choices"),
    ("never perform destructive operations autonomously", "confirm irreversible actions"),
    ("all code, code comments, commit messages", "English-only artifacts"),
    ("never hardcode credentials", "no secrets in source"),
    ("tdd is mandatory", "TDD"),
    ("in the same commit", "docs updated with the code"),
    ("no force-push on `main`", "no force-push on main"),
    ("before proposing a commit or opening a pr, verify", "self-review before commit"),
    ("one pr = one topic", "one topic per PR"),
]


def corpus_text() -> str:
    parts: list[str] = []
    for directory in CORPUS_DIRS:
        root = REPO_ROOT / directory
        if root.is_dir():
            parts.extend(path.read_text() for path in sorted(root.rglob("*.md")))
    return "\n".join(parts).lower()


@pytest.mark.parametrize(("phrase", "reason"), INVARIANTS, ids=[i[1] for i in INVARIANTS])
def test_normative_phrase_is_still_present(phrase: str, reason: str) -> None:
    assert phrase in corpus_text(), f"missing normative rule: {reason} ({phrase!r})"
