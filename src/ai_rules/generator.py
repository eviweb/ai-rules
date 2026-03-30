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


def generate_flat_file(repo_root: Path, source: Path, output: Path) -> None:
    """Generate a flat version of *source* (with imports resolved) at *output*."""
    content = resolve_imports(source, repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
