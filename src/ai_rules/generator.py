from __future__ import annotations

import re
from pathlib import Path

_IMPORT_RE = re.compile(r"^@rules/(.+)$")


def resolve_imports(source: Path, repo_root: Path) -> str:
    """Read *source* and inline every ``@rules/<file>`` import.

    Lines that match ``@rules/<file>`` are replaced with the content of
    ``<repo_root>/rules/<file>``.  All other lines are kept as-is.
    """
    lines: list[str] = []
    for line in source.read_text().splitlines():
        m = _IMPORT_RE.match(line.strip())
        if m:
            rules_file = repo_root / "rules" / m.group(1)
            lines.append(rules_file.read_text().rstrip())
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
