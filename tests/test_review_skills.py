from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEWING = REPO_ROOT / "skills" / "ai-rules-reviewing-changes"
RECEIVING = REPO_ROOT / "skills" / "ai-rules-receiving-code-review"


def _text(path: Path) -> str:
    return path.read_text()


def test_reviewing_builds_the_package_before_the_checklist() -> None:
    text = _text(REVIEWING / "SKILL.md")

    assert "`scripts/review-package.sh`" in text
    assert "untracked" in text
    assert text.index("## 1. Build the review package") < text.index("## 2. Self-review checklist")


def test_reviewing_reviews_against_the_intent_with_graded_findings() -> None:
    text = _text(REVIEWING / "SKILL.md")

    assert "[reviewer brief](references/reviewer-brief.md)" in text
    for grade in ("**Blocking**", "**Important**", "**Minor**"):
        assert grade in text
    assert "`ai-rules-receiving-code-review`" in text


def test_reviewing_is_derived_from_requesting_code_review() -> None:
    assert 'derived-from: "superpowers/requesting-code-review @ 22f0b46"' in _text(REVIEWING / "SKILL.md")


def test_reviewer_brief_is_read_only_and_ends_with_a_verdict() -> None:
    text = _text(REVIEWING / "references" / "reviewer-brief.md")

    assert "**Read-only.**" in text
    assert "### Declined to judge" in text
    assert "### Verdict" in text


def test_receiving_clarifies_every_item_before_implementing() -> None:
    text = _text(RECEIVING / "SKILL.md")

    assert "before implementing **anything**" in text
    assert "No performative agreement" in text


def test_receiving_verifies_external_feedback_and_defers_to_the_user() -> None:
    text = _text(RECEIVING / "SKILL.md")

    assert "**External reviewers**" in text
    assert "stop and ask the user" in text
    assert "YAGNI" in text


def test_receiving_fixes_test_first_and_never_commits() -> None:
    text = _text(RECEIVING / "SKILL.md")

    assert "`ai-rules-test-driven-development`" in text
    assert "never commit or push on your own" in text


def test_receiving_posts_platform_replies_only_with_the_user_agreement() -> None:
    text = _text(RECEIVING / "SKILL.md")

    assert "post only when the user agrees" in text
    assert "/replies" in text


def test_receiving_is_derived_from_the_pinned_upstream() -> None:
    assert 'derived-from: "superpowers/receiving-code-review @ 22f0b46"' in _text(RECEIVING / "SKILL.md")
