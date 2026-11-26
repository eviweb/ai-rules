from __future__ import annotations

import pytest

from ai_rules.guard import GuardParseError, SimpleCommand, normalize, parse_commands


def argvs(command: str) -> list[tuple[str, ...]]:
    return [simple.argv for simple in parse_commands(command)]


def test_parse_commands_splits_on_every_separator_outside_quotes() -> None:
    assert argvs("a && b || c ; d | e & f\ng") == [("a",), ("b",), ("c",), ("d",), ("e",), ("f",), ("g",)]


def test_parse_commands_keeps_separators_inside_quotes() -> None:
    assert argvs("echo 'a && b' \"c; d\"") == [("echo", "a && b", "c; d")]


def test_parse_commands_splits_pipes_with_stderr_and_compact_forms() -> None:
    assert argvs("a|&b;c&&d") == [("a",), ("b",), ("c",), ("d",)]


@pytest.mark.parametrize("opener", ["<<EOF", "<<'EOF'", '<<"EOF"', "<<-EOF"])
def test_parse_commands_attaches_heredoc_body_to_its_command(opener: str) -> None:
    command = f"python3 - {opener}\nx = 'git commit -m y'\nrm -rf z\nEOF\nls"

    parsed = parse_commands(command)

    assert parsed == [
        SimpleCommand(argv=("python3", "-"), stdin_text="x = 'git commit -m y'\nrm -rf z"),
        SimpleCommand(argv=("ls",)),
    ]


def test_parse_commands_accepts_an_indented_terminator_with_dash_heredoc() -> None:
    parsed = parse_commands("cat <<-EOF\n\tbody\n\tEOF\nls")

    assert [simple.argv for simple in parsed] == [("cat",), ("ls",)]


def test_parse_commands_rejects_an_unbalanced_quote() -> None:
    with pytest.raises(GuardParseError):
        parse_commands("echo 'unterminated")


def test_parse_commands_rejects_an_unterminated_heredoc() -> None:
    with pytest.raises(GuardParseError):
        parse_commands("cat <<EOF\nno end")


def test_parse_commands_ignores_empty_segments() -> None:
    assert argvs("a ;; b\n\n") == [("a",), ("b",)]


def test_normalize_drops_assignments_and_wrappers() -> None:
    argv = ("FOO=1", "env", "timeout", "5", "nice", "xargs", "-0", "/bin/rm", "-rf", "x")

    assert normalize(argv) == ("rm", "-rf", "x")


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (("command", "rm", "x"), ("rm", "x")),
        (("exec", "git", "status"), ("git", "status")),
        (("nohup", "./rm", "-r", "x"), ("rm", "-r", "x")),
        (("nice", "-n", "5", "rm", "x"), ("rm", "x")),
        (("timeout", "-s", "KILL", "5s", "rm", "x"), ("rm", "x")),
        (("env", "-i", "A=1", "rm", "x"), ("rm", "x")),
        (("xargs", "-n", "1", "-I", "{}", "rm", "{}"), ("rm", "{}")),
        (("ls",), ("ls",)),
        ((), ()),
    ],
)
def test_normalize_handles_wrapper_options(argv: tuple[str, ...], expected: tuple[str, ...]) -> None:
    assert normalize(argv) == expected


def test_parse_commands_keeps_a_heredoc_opened_by_an_empty_command() -> None:
    assert parse_commands("<<EOF\nbody\nEOF\nls") == [
        SimpleCommand(argv=(), stdin_text="body"),
        SimpleCommand(argv=("ls",)),
    ]


def test_parse_commands_ignores_comments() -> None:
    assert argvs("ls # rm -rf x\n# git push -f\npwd") == [("ls",), ("pwd",)]


def test_parse_commands_keeps_redirections_inside_their_command() -> None:
    assert argvs("make 2>&1 | tee log; cmd &>out") == [("make", "2>&1"), ("tee", "log"), ("cmd", "&>out")]


def test_parse_commands_reads_a_herestring_as_stdin_text() -> None:
    assert parse_commands('python3 <<< "import subprocess"') == [
        SimpleCommand(argv=("python3",), stdin_text="import subprocess"),
    ]


@pytest.mark.parametrize("command", ['echo "unterminated', "cat <<'EOF\nx\nEOF", "cat <<\nx"])
def test_parse_commands_rejects_malformed_quotes_and_delimiters(command: str) -> None:
    with pytest.raises(GuardParseError):
        parse_commands(command)


def test_normalize_stops_wrapper_options_at_double_dash() -> None:
    assert normalize(("env", "--", "rm", "-r", "x")) == ("rm", "-r", "x")


@pytest.mark.parametrize(
    ("argv", "expected"),
    [(("sudo", "-u", "root", "-E", "rm", "x"), ("rm", "x")), (("doas", "-u", "x", "rm", "x"), ("rm", "x"))],
)
def test_normalize_unwraps_privilege_wrappers(argv: tuple[str, ...], expected: tuple[str, ...]) -> None:
    assert normalize(argv) == expected
