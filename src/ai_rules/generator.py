from __future__ import annotations

import re
from pathlib import Path

_IMPORT_RE = re.compile(r"^@(core|rules|skills)/(.+)$")
_PATH_ITEM_RE = re.compile(r'^\s+-\s+["\']?(.*?)["\']?\s*$')


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return the ``paths:`` globs of a rule file and its body without frontmatter.

    Files without a leading ``---`` block are returned unchanged with no paths.
    Skill files carry other frontmatter keys: those are dropped too.
    """
    lines = text.split("\n")
    if lines[0].rstrip() != "---":
        return [], text
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    except StopIteration:
        return [], text
    paths: list[str] = []
    in_paths = False
    for line in lines[1:end]:
        if line.startswith("paths:"):
            in_paths = True
        elif in_paths:
            match = _PATH_ITEM_RE.match(line)
            if match is None:
                in_paths = False
            else:
                paths.append(match.group(1))
    return paths, "\n".join(lines[end + 1 :]).lstrip("\n")


def _inline(text: str) -> str:
    """Body of an imported file, with a one-line scope note when it has paths."""
    paths, body = split_frontmatter(text)
    body = body.rstrip()
    if not paths:
        return body
    note = "*Applies when working on: " + ", ".join(f"`{p}`" for p in paths) + ".*"
    head, separator, rest = body.partition("\n")
    if head.startswith("# "):
        return f"{head}\n\n{note}{separator}{rest}"
    return f"{note}\n\n{body}"


def resolve_imports(source: Path, repo_root: Path) -> str:
    """Read *source* and inline every ``@core/``, ``@rules/`` or ``@skills/`` import.

    Lines that match ``@<dir>/<file>`` are replaced with the content of
    ``<repo_root>/<dir>/<file>``, frontmatter removed (a rule's ``paths:`` become
    a one-line scope note). All other lines are kept as-is.
    """
    lines: list[str] = []
    for line in source.read_text().splitlines():
        m = _IMPORT_RE.match(line.strip())
        if m:
            rules_file = repo_root / m.group(1) / m.group(2)
            lines.append(_inline(rules_file.read_text()))
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def condense_content(content: str) -> str:
    """Strip fenced code blocks from *content* and collapse resulting blank lines.

    Agents that load rules as a flat file have limited context budgets.
    Removing illustrative code examples keeps the rules actionable while
    significantly reducing token count.
    """
    lines = content.splitlines()
    result: list[str] = []
    in_fence = False
    prev_blank = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        is_blank = stripped == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return "\n".join(result) + "\n"


def generate_flat_file(
    repo_root: Path, source: Path, output: Path, *, condense: bool = False
) -> None:
    """Generate a flat version of *source* (with imports resolved) at *output*.

    When *condense* is True, fenced code blocks are stripped to reduce size
    for agents with limited context budgets.
    """
    content = resolve_imports(source, repo_root)
    if condense:
        content = condense_content(content)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)


def verify_flat_file(
    repo_root: Path, source: Path, output: Path, *, condense: bool = False
) -> bool:
    """Return True if *output* is up to date with the resolved *source*.

    Returns False if *output* is missing or its content differs from what
    ``generate_flat_file`` would produce.
    """
    if not output.exists():
        return False
    expected = resolve_imports(source, repo_root)
    if condense:
        expected = condense_content(expected)
    return output.read_text() == expected
