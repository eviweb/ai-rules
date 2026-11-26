from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.guard import NO_DECISION, Decision, decide, find_repo_root

EXPECTED_COMMIT = "git commit -s -F .private/COMMIT_MESSAGE"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with a reviewed, non-empty commit message."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".private").mkdir()
    (tmp_path / ".private" / "COMMIT_MESSAGE").write_text("feat: something\n")
    (tmp_path / "sub").mkdir()
    return tmp_path


def action(command: str, cwd: Path) -> str | None:
    return decide(command, cwd).action


# --- R5: recursive rm, including nested and path forms ---


@pytest.mark.parametrize(
    "command",
    [
        "rm -r x",
        "rm -R x",
        "rm --recursive x",
        "rm -rf x",
        "rm -fR x",
        "rm -v -r x",
        "/bin/rm -fr /tmp/x",
        "bash -c 'rm -rf build'",
        "sh -c \"cd x && rm -rf y\"",
        "bash -lc 'rm -rf build'",
        "eval rm -rf x",
        "(cd x && rm -rf y)",
        "echo $(rm -rf x)",
        "FOO=1 timeout 5 rm -rf x",
    ],
)
def test_decide_denies_recursive_rm_in_every_form(command: str, repo: Path) -> None:
    decision = decide(command, repo)

    assert decision.action == "deny"
    assert "rm" in decision.reason


@pytest.mark.parametrize("command", ["rm file.txt", "rm -f file.txt", "rm -- -r", "bash -c 'ls'"])
def test_decide_lets_non_recursive_rm_and_harmless_nesting_through(command: str, repo: Path) -> None:
    assert decide(command, repo) == NO_DECISION


# --- R6: deletion without rm ---


@pytest.mark.parametrize(
    "command",
    ["find . -name '*.pyc' -delete", "find . -exec rm {} \\;", "find . -execdir /bin/rm {} +", "shred -u f"],
)
def test_decide_asks_for_deletion_without_rm(command: str, repo: Path) -> None:
    assert action(command, repo) == "ask"


def test_decide_lets_a_plain_find_through(repo: Path) -> None:
    assert decide("find . -name x -exec grep y {} +", repo) == NO_DECISION


# --- R7: git destructive forms behind global options ---


@pytest.mark.parametrize(
    "command",
    [
        "git push --force",
        "git push -f",
        "git push -uf origin x",
        "git push origin +main",
        "git -C ../other push --force origin main",
        "git --no-pager push origin +main:main",
        "git -c a=b reset --hard",
        "git reset --hard HEAD~1",
        "git clean -n",
        "git clean -fd",
        "git checkout -- f",
        "git branch -D x",
        "git branch --delete --force x",
        "git branch -d -f x",
    ],
)
def test_decide_denies_destructive_git_forms(command: str, repo: Path) -> None:
    assert action(command, repo) == "deny"


@pytest.mark.parametrize("command", ["git push --force-with-lease", "git push --force-with-lease=main:abc origin main"])
def test_decide_asks_for_force_with_lease(command: str, repo: Path) -> None:
    assert action(command, repo) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "git -C . status",
        "git push origin main",
        "git push -u origin feat/x",
        "git checkout main",
        "git branch -d x",
        "git reset --soft HEAD~1",
        "git log --oneline",
    ],
)
def test_decide_lets_ordinary_git_through(command: str, repo: Path) -> None:
    assert decide(command, repo) == NO_DECISION


# --- R8: agent commits only with the reviewed message ---


@pytest.mark.parametrize(
    "command",
    [
        EXPECTED_COMMIT,
        "git commit --signoff --file=.private/COMMIT_MESSAGE",
        "git commit -F .private/COMMIT_MESSAGE -s",
        "git commit --signoff --file .private/COMMIT_MESSAGE",
    ],
)
def test_decide_lets_the_reviewed_commit_reach_the_prompt(command: str, repo: Path) -> None:
    assert decide(command, repo) == NO_DECISION


def test_decide_resolves_the_message_path_from_a_subdirectory(repo: Path) -> None:
    assert decide("git commit -s -F ../.private/COMMIT_MESSAGE", repo / "sub") == NO_DECISION


def test_decide_follows_git_dash_c_for_the_message_path(repo: Path) -> None:
    assert decide("git -C .. commit -s -F .private/COMMIT_MESSAGE", repo / "sub") == NO_DECISION


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m fix",
        "git commit -s -F other.txt",
        "git commit --amend -s -F .private/COMMIT_MESSAGE",
        "git commit --no-verify -s -F .private/COMMIT_MESSAGE",
        "git commit -a -s -F .private/COMMIT_MESSAGE",
        "git commit -F .private/COMMIT_MESSAGE",
        "git commit -s",
    ],
)
def test_decide_denies_any_other_commit_form(command: str, repo: Path) -> None:
    decision = decide(command, repo)

    assert decision.action == "deny"
    assert EXPECTED_COMMIT in decision.reason


@pytest.mark.parametrize("content", [None, "", "  \n"])
def test_decide_denies_the_commit_when_the_message_is_missing_or_empty(content: str | None, repo: Path) -> None:
    message = repo / ".private" / "COMMIT_MESSAGE"
    if content is None:
        message.unlink()
    else:
        message.write_text(content)

    decision = decide(EXPECTED_COMMIT, repo)

    assert decision.action == "deny"
    assert EXPECTED_COMMIT in decision.reason


# --- R9: inline code with deletion or process primitives ---


@pytest.mark.parametrize(
    "command",
    [
        "python3 -c 'import shutil; shutil.rmtree(\"x\")'",
        "perl -e 'unlink \"x\"'",
        "node -e \"fs.rmdirSync('x')\"",
        "ruby -e 'system(\"rm -rf x\")'",
        "python3 - <<'EOF'\nimport os\nos.remove('x')\nEOF",
        "python3 -c 'import subprocess'",
    ],
)
def test_decide_asks_for_inline_code_with_deletion_primitives(command: str, repo: Path) -> None:
    assert action(command, repo) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "python3 -c 'print(1)'",
        "python3 - <<'EOF'\nfrom pathlib import Path\nPath('n.txt').write_text('use git commit -m x')\nEOF",
        "python3 script.py",
        "cat <<'EOF' > notes.txt\nos.remove is documented here\nEOF",
    ],
)
def test_decide_lets_harmless_inline_code_through(command: str, repo: Path) -> None:
    assert decide(command, repo) == NO_DECISION


# --- R4, R11, R12: nesting depth, precedence, unreadable commands ---


def test_decide_asks_beyond_three_levels_of_nesting(repo: Path) -> None:
    command = "bash -c \"sh -c 'bash -c \\\"sh -c ls\\\"'\""

    decision = decide(command, repo)

    assert decision.action == "ask"
    assert "could not be analysed" in decision.reason


def test_decide_asks_for_an_unbalanced_quote(repo: Path) -> None:
    decision = decide("echo 'oops", repo)

    assert decision.action == "ask"
    assert "could not be analysed" in decision.reason


def test_decide_prefers_deny_over_ask(repo: Path) -> None:
    assert action("git push --force-with-lease; rm -rf x", repo) == "deny"


def test_decision_reasons_are_never_empty(repo: Path) -> None:
    for command in ("rm -rf x", "shred f", "git push -f", "git commit -m x", "python3 -c 'import subprocess'"):
        assert decide(command, repo).reason


def test_no_decision_is_the_default() -> None:
    assert NO_DECISION == Decision(None)


# --- repository root ---


def test_find_repo_root_walks_up_to_the_git_entry(repo: Path) -> None:
    assert find_repo_root(repo / "sub") == str(repo)


def test_find_repo_root_accepts_a_git_file_for_worktrees(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text("gitdir: /elsewhere\n")

    assert find_repo_root(tmp_path) == str(tmp_path)


def test_find_repo_root_returns_none_outside_a_repository(tmp_path: Path) -> None:
    assert find_repo_root(tmp_path) is None


@pytest.mark.parametrize("command", ["git", "git --version", "bash script.sh", "eval"])
def test_decide_lets_bare_programs_through(command: str, repo: Path) -> None:
    assert decide(command, repo) == NO_DECISION


def test_decide_asks_for_inline_code_read_from_a_herestring(repo: Path) -> None:
    assert action('python3 <<< "import subprocess"', repo) == "ask"


# --- R5b: privilege elevation at any level ---


@pytest.mark.parametrize(
    "command",
    ["bash -c 'sudo rm -rf /x'", "sudo -u root ls", "doas rm -rf /x", "eval sudo ls", "env A=1 doas -u x ls"],
)
def test_decide_denies_sudo_and_doas_at_any_level(command: str, repo: Path) -> None:
    decision = decide(command, repo)

    assert decision.action == "deny"
    assert "sudo" in decision.reason


# --- R8: git global options that bypass hooks, signature or identity ---


@pytest.mark.parametrize(
    "command",
    [
        "git -c core.hooksPath=/dev/null commit -s -F .private/COMMIT_MESSAGE",
        "git -c commit.gpgSign=false commit -s -F .private/COMMIT_MESSAGE",
        "git -c user.email=x@y commit -s -F .private/COMMIT_MESSAGE",
        "bash -c 'git -c core.hookspath=/tmp commit -s -F .private/COMMIT_MESSAGE'",
    ],
)
def test_decide_denies_a_commit_behind_bypassing_global_options(command: str, repo: Path) -> None:
    decision = decide(command, repo)

    assert decision.action == "deny"
    assert EXPECTED_COMMIT in decision.reason


def test_decide_keeps_harmless_global_options_on_the_reviewed_commit(repo: Path) -> None:
    assert decide("git -c color.ui=never commit -s -F .private/COMMIT_MESSAGE", repo) == NO_DECISION
