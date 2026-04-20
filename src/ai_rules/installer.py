from __future__ import annotations

import re
import shutil
import tomllib
from datetime import datetime
from pathlib import Path

from ai_rules.agent import Agent, ConfigPatch, ConfigValue, Link

_BOOL_TOML = {True: "true", False: "false"}


def _backup_dir(install_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return install_path / f"backup-{timestamp}"


def _resolve_link(repo_root: Path, agent: Agent, link: Link) -> tuple[Path, Path]:
    source = (repo_root / link.source).resolve()
    target = agent.install_path / link.target
    return source, target


def _toml_format(value: ConfigValue) -> str:
    if isinstance(value, bool):
        return _BOOL_TOML[value]
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def _find_link_backup(install_path: Path, name: str) -> Path | None:
    """Return the most recent backup of *name* from any backup-* directory."""
    candidates = sorted(
        (d / name for d in install_path.glob("backup-*") if (d / name).exists()),
        key=lambda p: p.parent.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _cleanup_backup_dir(backup_dir: Path) -> None:
    """Remove *backup_dir* if it is empty."""
    if backup_dir.is_dir() and not any(backup_dir.iterdir()):
        backup_dir.rmdir()


def _find_toml_backup(target_file: Path) -> Path | None:
    """Return the most recent .bak file for *target_file*."""
    candidates = sorted(
        target_file.parent.glob(f"{target_file.name}.*.bak"),
        reverse=True,
    )
    return candidates[0] if candidates else None


def _patch_toml_file(
    target_file: Path, patch: ConfigPatch, dry_run: bool = False
) -> list[str]:
    """Ensure *patch.key* is set to *patch.value* in *target_file*.

    Backs up the file before any modification. Creates the file if absent.
    Only the root-level section is touched — keys inside [sections] are ignored.
    """
    formatted = _toml_format(patch.value)
    new_line = f"{patch.key} = {formatted}"
    actions: list[str] = []

    if target_file.exists():
        content = target_file.read_text()
        try:
            existing = tomllib.loads(content)
        except tomllib.TOMLDecodeError:
            existing = {}
        if existing.get(patch.key) == patch.value:
            actions.append(f"OK      {patch.file}: {patch.key} already set")
            return actions
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target_file.parent / f"{target_file.name}.{timestamp}.bak"
        actions.append(f"BACKUP  {patch.file} -> {backup.name}")
        if not dry_run:
            shutil.copy2(target_file, backup)
    else:
        content = ""

    # Split root section from the rest (first bare [section] header)
    section_match = re.search(r"^\[", content, re.MULTILINE)
    root = content[: section_match.start()] if section_match else content
    rest = content[section_match.start() :] if section_match else ""

    key_pattern = re.compile(rf"^{re.escape(patch.key)}\s*=.*$", re.MULTILINE)
    if key_pattern.search(root):
        new_root = key_pattern.sub(new_line, root)
    else:
        separator = "\n" if root and not root.endswith("\n") else ""
        new_root = root + separator + new_line + "\n"

    patched = new_root + rest
    actions.append(f"PATCH   {patch.file}: {patch.key} = {formatted}")
    if not dry_run:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(patched)

    return actions


def _unpatch_toml_file(
    target_file: Path, patch: ConfigPatch, dry_run: bool = False
) -> list[str]:
    """Remove *patch.key* from the root section of *target_file*.

    Used when no backup exists to restore from.
    """
    if not target_file.exists():
        return [f"SKIP    {patch.file}: not found"]
    content = target_file.read_text()
    try:
        existing = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        return [f"SKIP    {patch.file}: parse error"]
    if patch.key not in existing:
        return [f"OK      {patch.file}: {patch.key} not present"]

    key_pattern = re.compile(rf"^{re.escape(patch.key)}\s*=.*\n?", re.MULTILINE)
    new_content = key_pattern.sub("", content)
    if not dry_run:
        target_file.write_text(new_content)
    return [f"UNPATCH {patch.file}: removed {patch.key}"]


def install_agent(
    repo_root: Path, agent: Agent, dry_run: bool = False
) -> list[str]:
    """Deploy symlinks and apply config patches for an agent.

    Returns a list of human-readable action lines.
    """
    actions: list[str] = []
    backup_dir: Path | None = None

    if not dry_run:
        agent.install_path.mkdir(parents=True, exist_ok=True)

    for link in agent.links:
        source, target = _resolve_link(repo_root, agent, link)

        if not source.exists():
            actions.append(f"SKIP    {link.target}: source not found ({source})")
            continue

        if target.is_symlink():
            if target.resolve() == source:
                actions.append(f"OK      {link.target}: already linked")
            else:
                actions.append(f"UPDATE  {link.target}: re-linking to new source")
                if not dry_run:
                    target.unlink()
                    target.symlink_to(source)
            continue

        if target.exists():
            if backup_dir is None:
                backup_dir = _backup_dir(agent.install_path)
            actions.append(f"BACKUP  {link.target}: moving to {backup_dir.name}/")
            if not dry_run:
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), backup_dir / target.name)

        actions.append(f"LINK    {link.target}: {target} -> {source}")
        if not dry_run:
            target.symlink_to(source)

    for patch in agent.config_patches:
        target_file = agent.install_path / patch.file
        actions.extend(_patch_toml_file(target_file, patch, dry_run=dry_run))

    return actions


def remove_agent(
    repo_root: Path, agent: Agent, dry_run: bool = False
) -> list[str]:
    """Remove symlinks and revert config patches for an agent.

    For each symlink owned by ai-rules: removes it and restores the most
    recent backup if one exists. For each config patch: restores the most
    recent .bak file, or removes the patched key if no backup is found.

    Returns a list of human-readable action lines.
    """
    actions: list[str] = []

    for link in agent.links:
        source, target = _resolve_link(repo_root, agent, link)

        if not target.is_symlink() or target.resolve() != source:
            actions.append(f"SKIP    {link.target}: not managed by ai-rules")
            continue

        actions.append(f"UNLINK  {link.target}")
        if not dry_run:
            target.unlink()

        backup = _find_link_backup(agent.install_path, target.name)
        if backup:
            actions.append(f"RESTORE {link.target}: from {backup.parent.name}/")
            if not dry_run:
                shutil.move(str(backup), target)
                _cleanup_backup_dir(backup.parent)

    for patch in agent.config_patches:
        target_file = agent.install_path / patch.file
        bak = _find_toml_backup(target_file)
        if bak:
            actions.append(f"RESTORE {patch.file}: from {bak.name}")
            if not dry_run:
                shutil.copy2(bak, target_file)
                bak.unlink()
        else:
            actions.extend(_unpatch_toml_file(target_file, patch, dry_run=dry_run))

    return actions


def status_agent(repo_root: Path, agent: Agent) -> list[tuple[str, str]]:
    """Return the installation status of each declared link and config patch."""
    results: list[tuple[str, str]] = []

    for link in agent.links:
        source, target = _resolve_link(repo_root, agent, link)

        if not target.exists() and not target.is_symlink():
            results.append((link.target, "not installed"))
        elif target.is_symlink() and target.resolve() == source:
            results.append((link.target, "ok"))
        elif target.is_symlink():
            results.append((link.target, f"symlink mismatch -> {target.resolve()}"))
        else:
            results.append((link.target, "exists (not a symlink)"))

    for patch in agent.config_patches:
        target_file = agent.install_path / patch.file
        if not target_file.exists():
            results.append((patch.file, "not installed"))
            continue
        try:
            existing = tomllib.loads(target_file.read_text())
        except tomllib.TOMLDecodeError:
            results.append((patch.file, "parse error"))
            continue
        if existing.get(patch.key) == patch.value:
            results.append((patch.file, "ok"))
        else:
            current = existing.get(patch.key, "<missing>")
            results.append((patch.file, f"patch needed ({patch.key}={current})"))

    return results
