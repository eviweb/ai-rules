"""Skill format: strict frontmatter parser and integrity checks.

A skill is a folder ``skills/ai-rules-<topic>/`` holding a ``SKILL.md`` (YAML
frontmatter + Markdown body) and optionally ``references/`` and ``scripts/``.
The frontmatter is deliberately a small YAML subset (scalars and one level of
``metadata``) so that no YAML dependency is needed; anything the parser does
not understand is an error, never a silent guess.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

SKILL_FILE = "SKILL.md"
NAME_PREFIX = "ai-rules-"
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 300
MAX_SKILL_BYTES = 8 * 1024
DESCRIPTION_START = "Use when"
THIRD_PARTY_FILE = "THIRD_PARTY.md"

# Fields accepted by Claude Code, claude.ai and the Agent Skills format alike.
ALLOWED_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)

_KEY_PATTERN = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]+(.*))?$")
_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_LINK_PATTERN = re.compile(r"\]\(([^)\s]+)\)")
_BACKTICK_PATTERN = re.compile(r"`((?:references|scripts)/[^`\s]+)`")
_SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_PLAIN_FORBIDDEN_START = "[{&*!|>%@`"

FrontmatterValue = str | dict[str, str]


class SkillFormatError(ValueError):
    """Raised when a SKILL.md frontmatter cannot be parsed."""


@dataclass
class SkillInfo:
    name: str
    description: str
    size: int
    valid: bool


def _parse_scalar(value: str, line_number: int) -> str:
    where = f"line {line_number}"
    if value[0] in "\"'":
        quote = value[0]
        if len(value) < 2 or value[-1] != quote:
            raise SkillFormatError(f"{where}: unterminated quote")
        inner = value[1:-1]
        if quote in inner or "\\" in inner:
            raise SkillFormatError(
                f"{where}: escapes and nested quotes are unsupported in quoted values"
            )
        return inner
    if value[0] in _PLAIN_FORBIDDEN_START:
        raise SkillFormatError(f"{where}: unsupported YAML syntax, quote the value")
    if ": " in value or " #" in value or value.endswith(":"):
        raise SkillFormatError(
            f"{where}: plain value contains ': ' or ' #' or ends with ':', quote it"
        )
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, FrontmatterValue], str]:
    """Split *text* into its frontmatter fields and Markdown body.

    Supports ``key: value`` scalars (plain, single- or double-quoted, with no
    escapes) and one level of mapping, used for ``metadata``. Raises
    SkillFormatError for anything else, including duplicate keys.
    """
    lines = text.split("\n")
    if lines[0].rstrip() != "---":
        raise SkillFormatError("file must start with a '---' frontmatter line")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    except StopIteration:
        raise SkillFormatError("frontmatter is not closed by a '---' line") from None

    fields: dict[str, FrontmatterValue] = {}
    current_map: dict[str, str] | None = None

    for index in range(1, end):
        line_number = index + 1
        line = lines[index].rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if line.startswith(" "):
            if current_map is None or not line.startswith("  ") or line.startswith("   "):
                raise SkillFormatError(f"line {line_number}: unexpected indentation")
            match = _KEY_PATTERN.match(line[2:])
            if match is None or match.group(2) is None:
                raise SkillFormatError(f"line {line_number}: expected 'key: value'")
            key, value = match.group(1), match.group(2).strip()
            if key in current_map:
                raise SkillFormatError(f"line {line_number}: duplicate key '{key}'")
            current_map[key] = _parse_scalar(value, line_number)
            continue

        match = _KEY_PATTERN.match(line)
        if match is None:
            raise SkillFormatError(f"line {line_number}: expected 'key: value'")
        key, value = match.group(1), match.group(2)
        if key in fields:
            raise SkillFormatError(f"line {line_number}: duplicate key '{key}'")
        if value is None or not value.strip():
            current_map = {}
            fields[key] = current_map
        else:
            current_map = None
            fields[key] = _parse_scalar(value.strip(), line_number)

    return fields, "\n".join(lines[end + 1 :])


def discover_skills(skills_dir: Path) -> list[Path]:
    """Every directory under *skills_dir*, sorted by name."""
    if not skills_dir.is_dir():
        return []
    return sorted(p for p in skills_dir.iterdir() if p.is_dir())


def _check_name(folder: Path, name: object) -> list[str]:
    problems: list[str] = []
    if not isinstance(name, str) or not name:
        return ["frontmatter 'name' is missing"]
    if name != folder.name:
        problems.append(f"name '{name}' does not match folder '{folder.name}'")
    if not _NAME_PATTERN.match(name):
        problems.append(f"name '{name}' must be kebab-case (a-z, 0-9, single hyphens)")
    if len(name) > MAX_NAME_LENGTH:
        problems.append(f"name is longer than {MAX_NAME_LENGTH} characters")
    return problems


def _check_description(description: object) -> list[str]:
    if not isinstance(description, str) or not description:
        return ["frontmatter 'description' is missing"]
    problems: list[str] = []
    if not description.startswith(DESCRIPTION_START):
        problems.append(f"description must start with '{DESCRIPTION_START}'")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        problems.append(
            f"description is {len(description)} characters, over the "
            f"{MAX_DESCRIPTION_LENGTH} limit"
        )
    return problems


def _check_derived_from(metadata: dict[str, str], repo_root: Path | None) -> list[str]:
    if "derived-from" not in metadata:
        return []
    problems: list[str] = []
    derived_from = metadata["derived-from"]
    if not derived_from:
        problems.append("metadata 'derived-from' is empty")
    if not metadata.get("license-of-origin"):
        problems.append("derived skill needs metadata 'license-of-origin'")
    if repo_root is not None and derived_from:
        notice = repo_root / THIRD_PARTY_FILE
        if not notice.is_file():
            problems.append(f"derived skill needs {THIRD_PARTY_FILE} at the repository root")
        else:
            upstream = derived_from.split("/")[0].split("@")[0].strip().lower()
            if upstream and upstream not in notice.read_text().lower():
                problems.append(f"{THIRD_PARTY_FILE} does not mention '{upstream}'")
    return problems


def _check_references(folder: Path, body: str) -> list[str]:
    references: list[str] = []
    for target in _LINK_PATTERN.findall(body):
        if target.startswith("#") or _SCHEME_PATTERN.match(target):
            continue
        references.append(target.split("#")[0])
    references.extend(_BACKTICK_PATTERN.findall(body))

    problems: list[str] = []
    root = folder.resolve()
    for reference in dict.fromkeys(r for r in references if r):
        resolved = (folder / reference).resolve()
        if not resolved.is_relative_to(root):
            problems.append(f"reference '{reference}' points outside the skill folder")
        elif not resolved.exists():
            problems.append(f"referenced file not found: {reference}")
    return problems


def _is_shell_script(path: Path) -> bool:
    if path.suffix == ".sh":
        return True
    try:
        first_line = path.read_text(errors="ignore").split("\n", 1)[0]
    except OSError:
        return False
    return first_line.startswith("#!") and "sh" in first_line


def _check_scripts(folder: Path) -> list[str]:
    scripts_dir = folder / "scripts"
    if not scripts_dir.is_dir():
        return []
    shellcheck = shutil.which("shellcheck")
    problems: list[str] = []
    for script in sorted(p for p in scripts_dir.rglob("*") if p.is_file()):
        label = script.relative_to(folder).as_posix()
        if not script.stat().st_mode & 0o111:
            problems.append(f"{label} is not executable")
        if shellcheck and _is_shell_script(script):
            result = subprocess.run(
                [shellcheck, "--format=gcc", str(script)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                first = (result.stdout.strip().splitlines() or ["see shellcheck"])[0]
                problems.append(f"{label}: shellcheck failed: {first}")
    return problems


def verify_skill(folder: Path, repo_root: Path | None = None) -> list[str]:
    """Return the integrity problems of the skill in *folder* (empty if valid).

    *repo_root* enables the checks that look outside the skill folder
    (the ``THIRD_PARTY.md`` notice of derived skills).
    """
    skill_file = folder / SKILL_FILE
    if not skill_file.is_file():
        return [f"{SKILL_FILE} is missing"]

    raw = skill_file.read_bytes()
    try:
        fields, body = parse_frontmatter(raw.decode("utf-8"))
    except (SkillFormatError, UnicodeDecodeError) as exc:
        return [f"invalid frontmatter: {exc}"]

    problems: list[str] = []
    if not folder.name.startswith(NAME_PREFIX):
        problems.append(f"folder name must carry the '{NAME_PREFIX}' prefix")
    problems.extend(_check_name(folder, fields.get("name")))
    problems.extend(_check_description(fields.get("description")))
    for field_name in fields:
        if field_name not in ALLOWED_FIELDS:
            problems.append(f"unsupported field '{field_name}'")

    metadata = fields.get("metadata", {})
    if isinstance(metadata, dict):
        problems.extend(_check_derived_from(metadata, repo_root))
    else:
        problems.append("metadata must be a mapping of keys to values")

    if len(raw) > MAX_SKILL_BYTES:
        problems.append(
            f"{SKILL_FILE} is {len(raw)} bytes, over the {MAX_SKILL_BYTES // 1024} KiB limit"
        )
    problems.extend(_check_references(folder, body))
    problems.extend(_check_scripts(folder))
    return problems


def verify_skills(
    skills_dir: Path, repo_root: Path | None = None
) -> dict[str, list[str]]:
    """Map each invalid skill folder name to its problems."""
    result: dict[str, list[str]] = {}
    for folder in discover_skills(skills_dir):
        problems = verify_skill(folder, repo_root)
        if problems:
            result[folder.name] = problems
    return result


def describe_skill(folder: Path, repo_root: Path | None = None) -> SkillInfo:
    """Name, description and size of a skill, tolerating an invalid one."""
    skill_file = folder / SKILL_FILE
    name, description, size = folder.name, "", 0
    if skill_file.is_file():
        size = skill_file.stat().st_size
        try:
            fields, _ = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        except (SkillFormatError, UnicodeDecodeError):
            fields = {}
        raw_description = fields.get("description", "")
        description = raw_description if isinstance(raw_description, str) else ""
    return SkillInfo(
        name=name,
        description=description,
        size=size,
        valid=not verify_skill(folder, repo_root),
    )


__all__ = [
    "ALLOWED_FIELDS",
    "SkillFormatError",
    "SkillInfo",
    "describe_skill",
    "discover_skills",
    "parse_frontmatter",
    "verify_skill",
    "verify_skills",
]
