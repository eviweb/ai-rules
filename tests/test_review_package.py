from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "skills" / "ai-rules-reviewing-changes" / "scripts" / "review-package.sh"


def git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.org",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.org",
    }
    hooks = repo.parent / "no-hooks"
    hooks.mkdir(exist_ok=True)
    result = subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={hooks}", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with one commit on main and a feature branch checked out."""
    path = tmp_path / "project"
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    (path / ".gitignore").write_text(".private/\n*.log\n")
    (path / "app.py").write_text("def greet():\n    return 'hello'\n")
    git(path, "add", ".gitignore", "app.py")
    git(path, "commit", "-q", "-m", "chore: initial commit")
    git(path, "checkout", "-q", "-b", "feat/change")
    return path


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), *args], cwd=repo, capture_output=True, text=True, check=False)


def commits_section(text: str) -> str:
    return text.split("## Commits since the base", 1)[1].split("## Files changed", 1)[0]


def package_path(result: subprocess.CompletedProcess[str]) -> Path:
    match = re.search(r"wrote (\S+):", result.stdout)
    assert match, result.stdout + result.stderr
    return Path(match.group(1))


def test_package_holds_the_commits_since_the_merge_base_with_main(repo: Path) -> None:
    (repo / "app.py").write_text("def greet():\n    return 'hello, world'\n")
    git(repo, "commit", "-q", "-am", "feat: greet the world")

    result = run(repo)

    assert result.returncode == 0, result.stderr
    text = package_path(result).read_text()
    assert "feat: greet the world" in commits_section(text)
    assert "+    return 'hello, world'" in text
    assert "chore: initial commit" not in commits_section(text)


def test_package_is_written_under_private_reviews_by_default(repo: Path) -> None:
    (repo / "app.py").write_text("changed\n")

    path = package_path(run(repo))

    assert path.parent == repo / ".private" / "reviews"
    assert re.fullmatch(r"review-[0-9a-f]{7}-\d{8}-\d{6}\.md", path.name)


def test_package_includes_staged_unstaged_and_untracked_files(repo: Path) -> None:
    (repo / "staged.py").write_text("STAGED = 1\n")
    git(repo, "add", "staged.py")
    (repo / "app.py").write_text("UNSTAGED = 2\n")
    (repo / "new_module.py").write_text("UNTRACKED = 3\n")

    text = package_path(run(repo)).read_text()

    assert "+STAGED = 1" in text
    assert "+UNSTAGED = 2" in text
    assert "new_module.py" in text and "+UNTRACKED = 3" in text


def test_package_leaves_out_ignored_files(repo: Path) -> None:
    (repo / "app.py").write_text("changed\n")
    (repo / "debug.log").write_text("SECRET_LOG_LINE\n")

    text = package_path(run(repo)).read_text()

    assert "SECRET_LOG_LINE" not in text


def test_base_option_selects_another_base(repo: Path) -> None:
    (repo / "app.py").write_text("first\n")
    git(repo, "commit", "-q", "-am", "feat: first step")
    base = git(repo, "rev-parse", "HEAD").strip()
    (repo / "app.py").write_text("second\n")
    git(repo, "commit", "-q", "-am", "feat: second step")

    text = package_path(run(repo, "--base", base)).read_text()

    assert "feat: second step" in commits_section(text)
    assert "feat: first step" not in commits_section(text)


def test_output_option_writes_the_package_where_asked(repo: Path, tmp_path: Path) -> None:
    (repo / "app.py").write_text("changed\n")
    target = tmp_path / "out" / "package.md"

    result = run(repo, "--output", str(target))

    assert result.returncode == 0, result.stderr
    assert package_path(result) == target
    assert target.is_file()


def test_short_output_alias_is_accepted(repo: Path, tmp_path: Path) -> None:
    (repo / "app.py").write_text("changed\n")
    target = tmp_path / "short.md"

    assert package_path(run(repo, "-o", str(target))) == target


def test_an_interrupted_run_leaves_no_partial_package(repo: Path, tmp_path: Path) -> None:
    (repo / "app.py").write_text("changed\n")
    (repo / "unreadable.py").write_text("x\n")
    (repo / "unreadable.py").chmod(0)
    target = tmp_path / "partial.md"

    result = run(repo, "--output", str(target))

    (repo / "unreadable.py").chmod(0o644)
    assert result.returncode != 0
    assert not target.exists()
    assert list(tmp_path.glob("partial.md*")) == []


def test_falls_back_to_master_when_main_does_not_exist(repo: Path) -> None:
    git(repo, "branch", "-m", "main", "master")
    (repo / "app.py").write_text("changed\n")

    assert run(repo).returncode == 0


def test_running_it_leaves_the_repository_state_unchanged(repo: Path) -> None:
    (repo / "staged.py").write_text("STAGED = 1\n")
    git(repo, "add", "staged.py")
    (repo / "app.py").write_text("UNSTAGED = 2\n")
    (repo / "new_module.py").write_text("UNTRACKED = 3\n")
    before = git(repo, "status", "--porcelain")

    run(repo)

    assert git(repo, "status", "--porcelain") == before


def test_nothing_to_review_exits_3(repo: Path) -> None:
    result = run(repo)

    assert result.returncode == 3
    assert "nothing to review" in result.stderr


def test_outside_a_git_repository_exits_2(tmp_path: Path) -> None:
    result = run(tmp_path)

    assert result.returncode == 2
    assert "not a git repository" in result.stderr


def test_unknown_base_exits_2(repo: Path) -> None:
    result = run(repo, "--base", "no-such-ref")

    assert result.returncode == 2
    assert "no-such-ref" in result.stderr


def test_unknown_option_exits_2(repo: Path) -> None:
    assert run(repo, "--bogus").returncode == 2


def test_help_and_version_exit_zero(repo: Path) -> None:
    assert run(repo, "--help").returncode == 0
    assert run(repo, "-V").returncode == 0


def test_commits_section_says_none_before_the_first_commit(repo: Path) -> None:
    (repo / "app.py").write_text("changed\n")

    text = package_path(run(repo)).read_text()

    assert commits_section(text).strip() == "(none)"


def test_diff_fence_survives_markdown_code_blocks_in_the_change(repo: Path) -> None:
    (repo / "notes.md").write_text("```bash\necho hi\n```\n")

    text = package_path(run(repo)).read_text()

    assert "`````diff\n" in text
    assert text.rstrip().endswith("`````")
