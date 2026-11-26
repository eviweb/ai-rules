from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FINISHING = REPO_ROOT / "skills" / "ai-rules-finishing-a-branch" / "SKILL.md"
RELEASING = REPO_ROOT / "skills" / "ai-rules-releasing" / "SKILL.md"


def test_finishing_is_derived_from_the_pinned_upstream() -> None:
    assert 'derived-from: "superpowers/finishing-a-development-branch @ 22f0b46"' in FINISHING.read_text()


def test_finishing_verifies_the_tree_and_confirms_base_and_remote() -> None:
    text = FINISHING.read_text()

    assert "on this tree" in text
    assert "`git remote -v`" in text
    assert text.index("## 1. Verify") < text.index("## 3. Offer the ways to finish")


def test_finishing_gives_the_full_command_block_and_never_runs_it() -> None:
    text = FINISHING.read_text()

    for command in (
        "git commit -s -F .private/COMMIT_MESSAGE",
        "git push -u <remote> <branch>",
        "sleep 15",
        "gh pr checks --watch",
        "gh pr merge --merge",
        "git push <remote> --delete <branch>",
    ):
        assert command in text
    assert "the user runs it" in text


def test_finishing_discards_only_on_an_explicit_typed_confirmation() -> None:
    text = FINISHING.read_text()

    assert "## Discarding" in text
    assert "typing `discard`" in text


def test_releasing_tags_signed_with_the_tagging_message_after_the_merge() -> None:
    text = RELEASING.read_text()

    assert "git tag -s X.Y.Z -F .private/TAGGING_MESSAGE" in text
    assert "once it is on `main` and CI is green" in text


def test_releasing_keeps_the_release_rule_content() -> None:
    text = RELEASING.read_text()

    for kept in (
        "`.private/RELEASE_MESSAGE`",
        "No attribution line in release and tag messages",
        "`chore(release): bump version to X.Y.Z`",
        "Tag format: `X.Y.Z` (no `v` prefix)",
        "`X.Y.Z-dev`",
        "tea releases create",
    ):
        assert kept in text


def test_releasing_extracts_notes_with_its_own_script() -> None:
    text = RELEASING.read_text()

    assert "(scripts/extract-changelog.sh)" in text
    assert "--verify-tag" in text


def test_versioning_points_to_the_releasing_skill() -> None:
    text = (REPO_ROOT / "rules" / "versioning.md").read_text()

    assert "`ai-rules-releasing`" in text
    assert "release.md" not in text
