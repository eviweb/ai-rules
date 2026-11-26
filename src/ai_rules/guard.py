"""Pre-tool guard: decide whether an agent shell command must be denied or asked.

Spec: ``docs/specs/0001-pre-tool-guard.md``. Claude Code's permission rules
already match every subcommand of a compound command, but not the same program
invoked in another form (``bash -c``, ``/bin/rm``, ``git -C``). This module
closes those gaps. It never allows anything: it returns ``deny``, ``ask`` or no
decision, so it can only make the existing rules stricter.

Standard library only, and no import of other ``ai_rules`` modules: the hook
loads this file by path under ``python3 -I -S``. It runs before every shell
command of the agent, so it avoids slow imports (``dataclasses``, ``pathlib``,
``typing``): ``re`` is already loaded by ``json`` in the hook.
"""

from __future__ import annotations

import os
import re


class GuardParseError(ValueError):
    """The command cannot be analysed (unbalanced quote, unterminated here-document)."""


class _Value:
    """Small immutable value object (``dataclasses`` costs ~12 ms to import)."""

    __slots__: tuple[str, ...] = ()

    def _fields(self) -> tuple[object, ...]:
        return tuple(getattr(self, name) for name in self.__slots__)

    def __eq__(self, other: object) -> bool:
        return type(other) is type(self) and other._fields() == self._fields()

    def __hash__(self) -> int:
        return hash(self._fields())

    def __repr__(self) -> str:
        values = ", ".join(f"{name}={getattr(self, name)!r}" for name in self.__slots__)
        return f"{type(self).__name__}({values})"


class SimpleCommand(_Value):
    """One command of a command line, with the text it reads from here-documents."""

    __slots__ = ("argv", "stdin_text")

    def __init__(self, argv: tuple[str, ...], stdin_text: str = "") -> None:
        self.argv = argv
        self.stdin_text = stdin_text


# --- parsing ---

_SEPARATOR_CHARS = ";|&()`"
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


class _Heredoc:
    __slots__ = ("delimiter", "strip_tabs", "command_index")

    def __init__(self, delimiter: str, strip_tabs: bool, command_index: int) -> None:
        self.delimiter = delimiter
        self.strip_tabs = strip_tabs
        self.command_index = command_index


class _Scanner:
    """Split a command line into simple commands, outside quotes."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.commands: list[list[str]] = []
        self.stdin: list[list[str]] = []
        self.words: list[str] = []
        self.word: list[str] = []
        self.in_word = False
        self.pending: list[_Heredoc] = []
        self.herestring_next = False
        # Text read by the command being built (here-strings, here-documents);
        # None while it reads none.
        self.pending_stdin: list[str] | None = None

    # word and command boundaries

    def end_word(self) -> None:
        if self.in_word:
            word = "".join(self.word)
            if self.herestring_next:
                self._stdin_of_current().append(word)
                self.herestring_next = False
            else:
                self.words.append(word)
        self.word = []
        self.in_word = False

    def end_command(self) -> None:
        self.end_word()
        if self.words or self.pending_stdin is not None:
            self.commands.append(self.words)
            self.stdin.append(self.pending_stdin or [])
        self.words = []
        self.pending_stdin = None

    def _stdin_of_current(self) -> list[str]:
        if self.pending_stdin is None:
            self.pending_stdin = []
        return self.pending_stdin

    def add(self, char: str) -> None:
        self.word.append(char)
        self.in_word = True

    # scanning

    def scan(self) -> list[SimpleCommand]:
        text = self.text
        while self.pos < len(text):
            char = text[self.pos]
            if char == "'":
                self._single_quoted()
            elif char == '"':
                self._double_quoted()
            elif char == "\\":
                self._escaped()
            elif char == "\n":
                self.end_command()
                self.pos += 1
                self._read_heredoc_bodies()
            elif char in " \t":
                self.end_word()
                self.pos += 1
            elif char == "#" and not self.in_word:
                end = text.find("\n", self.pos)
                self.pos = len(text) if end == -1 else end
            elif char == "<" and text.startswith("<<", self.pos):
                self._heredoc_operator()
            elif char == "&" and self._is_redirection_ampersand():
                self.add(char)
                self.pos += 1
            elif char == "$" and text.startswith("$(", self.pos):
                self.end_command()
                self.pos += 2
            elif char in _SEPARATOR_CHARS:
                self.end_command()
                self.pos += 1
            else:
                self.add(char)
                self.pos += 1
        if self.pending:
            raise GuardParseError(f"unterminated here-document: {self.pending[0].delimiter}")
        self.end_command()
        return [
            SimpleCommand(tuple(argv), "\n".join(stdin))
            for argv, stdin in zip(self.commands, self.stdin, strict=True)
        ]

    def _single_quoted(self) -> None:
        end = self.text.find("'", self.pos + 1)
        if end == -1:
            raise GuardParseError("unbalanced single quote")
        self.word.extend(self.text[self.pos + 1 : end])
        self.in_word = True
        self.pos = end + 1

    def _double_quoted(self) -> None:
        pos = self.pos + 1
        self.in_word = True
        while pos < len(self.text):
            char = self.text[pos]
            if char == '"':
                self.pos = pos + 1
                return
            if char == "\\" and pos + 1 < len(self.text) and self.text[pos + 1] in '"\\$`\n':
                if self.text[pos + 1] != "\n":
                    self.word.append(self.text[pos + 1])
                pos += 2
                continue
            self.word.append(char)
            pos += 1
        raise GuardParseError("unbalanced double quote")

    def _escaped(self) -> None:
        if self.pos + 1 < len(self.text):
            following = self.text[self.pos + 1]
            if following != "\n":  # a backslash-newline is a line continuation
                self.add(following)
        self.pos += 2

    def _is_redirection_ampersand(self) -> bool:
        before = self.text[self.pos - 1] if self.pos > 0 else ""
        after = self.text[self.pos + 1] if self.pos + 1 < len(self.text) else ""
        return before in "<>" or (after == ">" and not self.text.startswith("&&", self.pos))

    def _heredoc_operator(self) -> None:
        text = self.text
        if text.startswith("<<<", self.pos):
            self.end_word()
            self.herestring_next = True
            self.pos += 3
            return
        self.end_word()
        pos = self.pos + 2
        strip_tabs = text.startswith("-", pos)
        if strip_tabs:
            pos += 1
        while pos < len(text) and text[pos] in " \t":
            pos += 1
        delimiter: list[str] = []
        while pos < len(text) and text[pos] not in " \t\n;|&()<>":
            if text[pos] in "'\"":
                quote = text[pos]
                end = text.find(quote, pos + 1)
                if end == -1:
                    raise GuardParseError("unbalanced quote in here-document delimiter")
                delimiter.extend(text[pos + 1 : end])
                pos = end + 1
            elif text[pos] == "\\":
                pos += 1
            else:
                delimiter.append(text[pos])
                pos += 1
        if not delimiter:
            raise GuardParseError("here-document without a delimiter")
        self.pending.append(_Heredoc("".join(delimiter), strip_tabs, len(self.commands)))
        self._stdin_of_current()
        self.pos = pos

    def _read_heredoc_bodies(self) -> None:
        while self.pending:
            heredoc = self.pending.pop(0)
            lines: list[str] = []
            while True:
                if self.pos >= len(self.text):
                    raise GuardParseError(f"unterminated here-document: {heredoc.delimiter}")
                end = self.text.find("\n", self.pos)
                line = self.text[self.pos :] if end == -1 else self.text[self.pos : end]
                self.pos = len(self.text) if end == -1 else end + 1
                candidate = line.lstrip("\t") if heredoc.strip_tabs else line
                if candidate == heredoc.delimiter:
                    break
                lines.append(candidate)
            self.stdin[heredoc.command_index].append("\n".join(lines))


def parse_commands(command: str) -> list[SimpleCommand]:
    """Split *command* into simple commands; raise ``GuardParseError`` if it cannot."""
    return [simple for simple in _Scanner(command).scan() if simple.argv or simple.stdin_text]


# --- normalization ---

_KEYWORDS = {"!", "{", "}", "if", "then", "else", "elif", "fi", "do", "done", "while", "until", "time"}
# Wrapper -> options that take a separate argument.
_WRAPPERS: dict[str, set[str]] = {
    "env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
    "command": set(),
    "exec": {"-a"},
    "nohup": set(),
    "nice": {"-n", "--adjustment"},
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "xargs": {
        "-a", "--arg-file", "-d", "--delimiter", "-E", "-I", "-L", "--max-lines",
        "-n", "--max-args", "-P", "--max-procs", "-s", "--max-chars",
    },
    "sudo": {"-u", "--user", "-g", "--group", "-h", "--host", "-p", "--prompt", "-C", "--close-from",
             "-D", "--chdir", "-r", "--role", "-t", "--type", "-U", "--other-user", "-T", "--command-timeout"},
    "doas": {"-u", "-C"},
}
PRIVILEGE_WRAPPERS = {"sudo", "doas"}


def _skip_options(argv: tuple[str, ...], start: int, with_argument: set[str]) -> int:
    index = start
    while index < len(argv):
        word = argv[index]
        if word == "--":
            return index + 1
        if word.startswith("-") and len(word) > 1:
            index += 2 if word in with_argument else 1
        else:
            return index
    return index


def normalize(argv: tuple[str, ...]) -> tuple[str, ...]:
    """Drop assignments, shell keywords and wrappers; reduce a program path to its name."""
    return _unwrap(argv)[0]


def _unwrap(argv: tuple[str, ...]) -> tuple[tuple[str, ...], frozenset[str]]:
    """Return the normalized command and the wrappers that were dropped."""
    wrappers = set()
    index = 0
    while index < len(argv):
        word = argv[index]
        if _ASSIGNMENT.match(word) or word in _KEYWORDS:
            index += 1
        elif word in _WRAPPERS:
            wrappers.add(word)
            index = _skip_options(argv, index + 1, _WRAPPERS[word])
            if word == "env":
                while index < len(argv) and _ASSIGNMENT.match(argv[index]):
                    index += 1
            elif word == "timeout" and index < len(argv):
                index += 1  # the duration
        else:
            break
    rest = argv[index:]
    if rest and "/" in rest[0]:
        rest = (rest[0].rsplit("/", 1)[1], *rest[1:])
    return rest, frozenset(wrappers)


# --- decisions ---


class Decision(_Value):
    """``deny`` or ``ask`` with the reason given to the agent; ``None`` leaves it to the rules."""

    __slots__ = ("action", "reason")

    def __init__(self, action: str | None, reason: str = "") -> None:
        self.action = action
        self.reason = reason


NO_DECISION = Decision(None)

MAX_NESTING = 3
EXPECTED_COMMIT = "git commit -s -F .private/COMMIT_MESSAGE"
COMMIT_MESSAGE_PATH = (".private", "COMMIT_MESSAGE")
SHELLS = {"bash", "sh", "zsh", "dash"}
INLINE_CODE_INTERPRETERS = re.compile(r"^(python[0-9.]*|perl|ruby|node)$")
INLINE_CODE_OPTIONS = {"-c", "-e", "-E", "--eval", "-p", "--print"}
INLINE_CODE_PRIMITIVES = ("rmtree", "unlink", "remove", "rmdir", "os.system", "subprocess", "rm -")
GIT_OPTIONS_WITH_ARGUMENT = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

_UNREADABLE = "the command could not be analysed ({}); ask the user to confirm it"


def find_repo_root(cwd: str | os.PathLike[str]) -> str | None:
    """Return the closest directory holding ``.git`` (directory or worktree file)."""
    directory = os.path.abspath(cwd)
    while True:
        if os.path.exists(os.path.join(directory, ".git")):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


def _strictest(decisions: list[Decision]) -> Decision:
    for wanted in ("deny", "ask"):
        for decision in decisions:
            if decision.action == wanted:
                return decision
    return NO_DECISION


def _short_options(args: tuple[str, ...]) -> str:
    """Letters of the short option clusters before ``--`` (``-rf -v`` gives ``rfv``)."""
    letters = []
    for arg in args:
        if arg == "--":
            break
        if arg.startswith("-") and not arg.startswith("--"):
            letters.append(arg[1:])
    return "".join(letters)


def _long_options(args: tuple[str, ...]) -> set[str]:
    options = set()
    for arg in args:
        if arg == "--":
            break
        if arg.startswith("--"):
            options.add(arg.split("=", 1)[0])
    return options


def _decide_rm(args: tuple[str, ...]) -> Decision:
    if "r" in _short_options(args).lower() or "--recursive" in _long_options(args):
        return Decision("deny", "recursive rm is denied (also through bash -c, eval or a path such as /bin/rm): "
                                "ask the user to run it, or remove the files one by one")
    return NO_DECISION


def _decide_find(args: tuple[str, ...]) -> Decision:
    if "-delete" in args:
        return Decision("ask", "find -delete removes files: confirm the selection with the user")
    for index, arg in enumerate(args[:-1]):
        if arg in {"-exec", "-execdir", "-ok", "-okdir"} and normalize(args[index + 1 :])[:1] == ("rm",):
            return Decision("ask", "find -exec rm removes files: confirm the selection with the user")
    return NO_DECISION


class _GitCall(_Value):
    """A git invocation once its global options are skipped."""

    __slots__ = ("subcommand", "args", "directory", "config_keys")

    def __init__(self, subcommand: str, args: tuple[str, ...], directory: str, config_keys: tuple[str, ...]) -> None:
        self.subcommand = subcommand
        self.args = args
        self.directory = directory
        self.config_keys = config_keys


def _git_call(args: tuple[str, ...], cwd: str) -> _GitCall:
    """Skip git's global options, following ``-C`` and recording the keys set with ``-c``."""
    index = 0
    directory = cwd
    config_keys = []
    while index < len(args) and args[index].startswith("-"):
        option = args[index]
        if option in GIT_OPTIONS_WITH_ARGUMENT:
            value = args[index + 1] if index + 1 < len(args) else ""
            if option == "-C":
                directory = os.path.realpath(os.path.join(directory, value))
            elif option == "-c":
                config_keys.append(value.split("=", 1)[0].lower())
            index += 2
        else:
            index += 1
    if index >= len(args):
        return _GitCall("", (), directory, tuple(config_keys))
    return _GitCall(args[index], args[index + 1 :], directory, tuple(config_keys))


def _bypasses_commit_checks(config_keys: tuple[str, ...]) -> bool:
    """True when ``-c`` would skip the commit hooks, the signature or the identity."""
    return any(key in {"core.hookspath", "commit.gpgsign"} or key.startswith("user.") for key in config_keys)


def _decide_git_push(args: tuple[str, ...]) -> Decision:
    longs = _long_options(args)
    positional = [arg for arg in args if not arg.startswith("-")]
    if "--force" in longs or "f" in _short_options(args) or any(arg.startswith("+") for arg in positional):
        return Decision("deny", "force-push is denied (--force, -f or a +refspec): "
                                "the user decides and runs it")
    if "--force-with-lease" in longs:
        return Decision("ask", "git push --force-with-lease rewrites the remote branch: confirm with the user")
    return NO_DECISION


def _commit_message_file(args: tuple[str, ...]) -> tuple[bool, str | None, bool]:
    """Return (signed off, message file, only allowed options) for ``git commit`` arguments."""
    signoff = False
    message_file = None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in {"-s", "--signoff"}:
            signoff = True
        elif arg in {"-F", "--file"} and index + 1 < len(args):
            message_file = args[index + 1]
            index += 1
        elif arg.startswith("--file="):
            message_file = arg.split("=", 1)[1]
        else:
            return signoff, message_file, False
        index += 1
    return signoff, message_file, True


def _decide_git_commit(args: tuple[str, ...], directory: str, config_keys: tuple[str, ...]) -> Decision:
    denied = Decision("deny", f"the agent may only run `{EXPECTED_COMMIT}`, with the message the user "
                              "reviewed in .private/COMMIT_MESSAGE; otherwise propose the commit and let the user run it")
    signoff, message_file, only_allowed = _commit_message_file(args)
    root = find_repo_root(directory)
    if not (signoff and message_file and only_allowed and root) or _bypasses_commit_checks(config_keys):
        return denied
    expected = os.path.realpath(os.path.join(root, *COMMIT_MESSAGE_PATH))
    if os.path.realpath(os.path.join(directory, message_file)) != expected:
        return denied
    if not os.path.isfile(expected):
        return denied
    with open(expected, encoding="utf-8") as message:
        if not message.read().strip():
            return denied
    return NO_DECISION


def _decide_git(args: tuple[str, ...], cwd: str) -> Decision:
    call = _git_call(args, cwd)
    subcommand, rest = call.subcommand, call.args
    if subcommand == "push":
        return _decide_git_push(rest)
    if subcommand == "commit":
        return _decide_git_commit(rest, call.directory, call.config_keys)
    destructive = (
        (subcommand == "reset" and "--hard" in rest)
        or subcommand == "clean"
        or (subcommand == "checkout" and "--" in rest)
        or (subcommand == "branch" and _is_forced_branch_delete(rest))
    )
    if destructive:
        return Decision("deny", f"git {subcommand} in this form discards work and is denied: "
                                "the user decides and runs it")
    return NO_DECISION


def _is_forced_branch_delete(args: tuple[str, ...]) -> bool:
    shorts = _short_options(args)
    longs = _long_options(args)
    deleting = "d" in shorts or "--delete" in longs
    forced = "f" in shorts or "--force" in longs
    return "D" in shorts or (deleting and forced)


def _inline_code(args: tuple[str, ...], stdin_text: str) -> str:
    parts = [args[index + 1] for index, arg in enumerate(args[:-1]) if arg in INLINE_CODE_OPTIONS]
    if stdin_text:
        parts.append(stdin_text)
    return "\n".join(parts)


def _decide_inline_code(args: tuple[str, ...], stdin_text: str) -> Decision:
    code = _inline_code(args, stdin_text)
    found = [primitive for primitive in INLINE_CODE_PRIMITIVES if primitive in code]
    if found:
        return Decision("ask", f"inline code uses {', '.join(found)}: confirm with the user")
    return NO_DECISION


def _nested_command(program: str, args: tuple[str, ...]) -> str | None:
    """Return the command string run by ``bash -c`` or ``eval``, if any."""
    if program == "eval":
        return " ".join(args)
    for index, arg in enumerate(args):
        if arg.startswith("-") and not arg.startswith("--") and "c" in arg[1:]:
            return args[index + 1] if index + 1 < len(args) else ""
        if not arg.startswith("-"):
            return None
    return None


def _decide_text(command: str, cwd: str, depth: int) -> Decision:
    if depth > MAX_NESTING:
        return Decision("ask", _UNREADABLE.format(f"more than {MAX_NESTING} nested shells"))
    try:
        commands = parse_commands(command)
    except GuardParseError as error:
        return Decision("ask", _UNREADABLE.format(error))
    return _strictest([_decide_simple(simple, cwd, depth) for simple in commands])


def _decide_simple(simple: SimpleCommand, cwd: str, depth: int) -> Decision:
    argv, wrappers = _unwrap(simple.argv)
    if wrappers & PRIVILEGE_WRAPPERS:
        return Decision("deny", "sudo and doas are denied for the agent (also inside bash -c or eval): "
                                "the user runs privileged commands")
    if not argv:
        return NO_DECISION
    program, args = argv[0], argv[1:]
    if program in SHELLS or program == "eval":
        nested = _nested_command(program, args)
        return NO_DECISION if nested is None else _decide_text(nested, cwd, depth + 1)
    if program == "rm":
        return _decide_rm(args)
    if program == "find":
        return _decide_find(args)
    if program == "shred":
        return Decision("ask", "shred destroys file contents: confirm with the user")
    if program == "git":
        return _decide_git(args, cwd)
    if INLINE_CODE_INTERPRETERS.match(program):
        return _decide_inline_code(args, simple.stdin_text)
    return NO_DECISION


def decide(command: str, cwd: str | os.PathLike[str]) -> Decision:
    """Decide on a shell command the agent is about to run from *cwd*."""
    return _decide_text(command, os.fspath(cwd), depth=0)
