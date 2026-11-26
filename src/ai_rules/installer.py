from __future__ import annotations

import json
import os
import re
import shutil
import tomllib
from datetime import datetime
from pathlib import Path

from ai_rules.agent import Agent, ConfigPatch, ConfigValue, Link, SkillDir
from ai_rules.settings_merge import merge_settings, status_settings, unmerge_settings

_BOOL_TOML = {True: "true", False: "false"}


def _xdg_backup_dir(agent_key: str) -> Path:
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "ai-rules" / "backups" / agent_key


def _backup_dir(agent_key: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return _xdg_backup_dir(agent_key) / f"backup-{timestamp}"


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


def _find_link_backup(agent_key: str, name: str) -> Path | None:
    """Return the most recent backup of *name* from the XDG backup dir."""
    backup_root = _xdg_backup_dir(agent_key)
    candidates = sorted(
        (d / name for d in backup_root.glob("backup-*") if (d / name).exists()),
        key=lambda p: p.parent.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _cleanup_backup_dir(backup_dir: Path) -> None:
    """Remove *backup_dir* if it is empty."""
    if backup_dir.is_dir() and not any(backup_dir.iterdir()):
        backup_dir.rmdir()


def _find_toml_backup(target_file: Path, agent_key: str) -> Path | None:
    """Return the most recent .bak file for *target_file* from the XDG backup dir."""
    backup_root = _xdg_backup_dir(agent_key)
    candidates = sorted(
        backup_root.glob(f"{target_file.name}.*.bak"),
        reverse=True,
    )
    return candidates[0] if candidates else None


def _patch_toml_file(
    target_file: Path, patch: ConfigPatch, agent_key: str, dry_run: bool = False
) -> list[str]:
    """Ensure *patch.key* is set to *patch.value* in *target_file*.

    Backs up the file to the XDG state dir before any modification.
    Creates the file if absent. Only the root-level section is touched.
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
        backup_dir = _xdg_backup_dir(agent_key)
        backup = backup_dir / f"{target_file.name}.{timestamp}.bak"
        actions.append(f"BACKUP  {patch.file} -> {backup.name}")
        if not dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)
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


def _skill_target_root(agent: Agent, skill_dir: SkillDir) -> Path:
    """Directory receiving the skill links.

    Relative targets live under the agent's install_dir; ``~`` and absolute
    targets point elsewhere (Codex reads user skills from ``~/.agents/skills``).
    """
    return agent.install_path / Path(skill_dir.target).expanduser()


def _skill_names(source_dir: Path) -> list[str]:
    """Names of the skill folders in *source_dir* (those holding a SKILL.md)."""
    if not source_dir.is_dir():
        return []
    return sorted(
        d.name for d in source_dir.iterdir() if (d / "SKILL.md").is_file()
    )


def _owned_skill_links(source_dir: Path, target_root: Path) -> list[Path]:
    """Symlinks in *target_root* that point into *source_dir* (live or dangling)."""
    if not target_root.is_dir() or target_root.is_symlink():
        return []
    source_dir = source_dir.resolve()
    return sorted(
        entry
        for entry in target_root.iterdir()
        if entry.is_symlink() and entry.resolve().parent == source_dir
    )


def _install_skill_dir(
    repo_root: Path,
    agent: Agent,
    skill_dir: SkillDir,
    dry_run: bool,
) -> list[str]:
    source_dir = (repo_root / skill_dir.source).resolve()
    target_root = _skill_target_root(agent, skill_dir)
    label = skill_dir.target

    if not source_dir.is_dir():
        return [f"SKIP    {label}: source not found ({source_dir})"]
    if target_root.is_symlink():
        return [f"SKIP    {label}: target is a symlink, refusing to write through it"]

    actions: list[str] = []
    backup_dir: Path | None = None
    names = _skill_names(source_dir)

    for entry in _owned_skill_links(source_dir, target_root):
        if entry.name in names:
            continue
        actions.append(f"UNLINK  {label}/{entry.name}: skill removed from repository")
        if not dry_run:
            entry.unlink()

    if names and not dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    for name in names:
        source = source_dir / name
        target = target_root / name
        item = f"{label}/{name}"

        if target.is_symlink():
            if target.resolve() == source:
                actions.append(f"OK      {item}: already linked")
            else:
                actions.append(f"UPDATE  {item}: re-linking to new source")
                if not dry_run:
                    target.unlink()
                    target.symlink_to(source)
            continue

        if target.exists():
            if backup_dir is None:
                backup_dir = _backup_dir(agent.key)
            actions.append(f"BACKUP  {item}: moving to {backup_dir.name}/")
            if not dry_run:
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), backup_dir / target.name)

        actions.append(f"LINK    {item}: {target} -> {source}")
        if not dry_run:
            target.symlink_to(source)

    return actions


def _remove_skill_dir(
    repo_root: Path,
    agent: Agent,
    skill_dir: SkillDir,
    dry_run: bool,
) -> list[str]:
    source_dir = (repo_root / skill_dir.source).resolve()
    target_root = _skill_target_root(agent, skill_dir)
    label = skill_dir.target
    actions: list[str] = []

    for entry in _owned_skill_links(source_dir, target_root):
        actions.append(f"UNLINK  {label}/{entry.name}")
        if not dry_run:
            entry.unlink()
        backup = _find_link_backup(agent.key, entry.name)
        if backup:
            actions.append(f"RESTORE {label}/{entry.name}: from {backup.parent.name}/")
            if not dry_run:
                shutil.move(str(backup), entry)
                _cleanup_backup_dir(backup.parent)

    if not actions:
        actions.append(f"SKIP    {label}: no skill managed by ai-rules")
    return actions


def _status_skill_dir(
    repo_root: Path, agent: Agent, skill_dir: SkillDir
) -> list[tuple[str, str]]:
    source_dir = (repo_root / skill_dir.source).resolve()
    target_root = _skill_target_root(agent, skill_dir)
    label = skill_dir.target
    results: list[tuple[str, str]] = []
    names = _skill_names(source_dir)

    for name in names:
        source = source_dir / name
        target = target_root / name
        item = f"{label}/{name}"
        if not target.exists() and not target.is_symlink():
            results.append((item, "not installed"))
        elif target.is_symlink() and target.resolve() == source:
            results.append((item, "ok"))
        elif target.is_symlink():
            results.append((item, f"symlink mismatch -> {target.resolve()}"))
        else:
            results.append((item, "exists (not a symlink)"))

    for entry in _owned_skill_links(source_dir, target_root):
        if entry.name not in names:
            results.append(
                (f"{label}/{entry.name}", "stale (skill removed from repository)")
            )
    return results


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
                backup_dir = _backup_dir(agent.key)
            actions.append(f"BACKUP  {link.target}: moving to {backup_dir.name}/")
            if not dry_run:
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), backup_dir / target.name)

        actions.append(f"LINK    {link.target}: {target} -> {source}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source)

    for skill_dir in agent.skill_dirs:
        actions.extend(_install_skill_dir(repo_root, agent, skill_dir, dry_run))

    for patch in agent.config_patches:
        target_file = agent.install_path / patch.file
        actions.extend(_patch_toml_file(target_file, patch, agent.key, dry_run=dry_run))

    for settings_merge in agent.settings_merges:
        actions.extend(merge_settings(repo_root, agent, settings_merge, dry_run=dry_run))

    return actions


def remove_agent(
    repo_root: Path, agent: Agent, dry_run: bool = False
) -> list[str]:
    """Remove symlinks and revert config patches for an agent.

    For each symlink owned by ai-rules: removes it and restores the most
    recent backup from the XDG state dir if one exists. For each config patch:
    restores the most recent .bak file, or removes the patched key if no
    backup is found.

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

        backup = _find_link_backup(agent.key, target.name)
        if backup:
            actions.append(f"RESTORE {link.target}: from {backup.parent.name}/")
            if not dry_run:
                shutil.move(str(backup), target)
                _cleanup_backup_dir(backup.parent)

    for skill_dir in agent.skill_dirs:
        actions.extend(_remove_skill_dir(repo_root, agent, skill_dir, dry_run))

    for patch in agent.config_patches:
        target_file = agent.install_path / patch.file
        bak = _find_toml_backup(target_file, agent.key)
        if bak:
            actions.append(f"RESTORE {patch.file}: from {bak.name}")
            if not dry_run:
                shutil.copy2(bak, target_file)
                bak.unlink()
        else:
            actions.extend(_unpatch_toml_file(target_file, patch, dry_run=dry_run))

    for settings_merge in agent.settings_merges:
        actions.extend(unmerge_settings(repo_root, agent, settings_merge, dry_run=dry_run))

    return actions


def migrate_agent_backups(agent: Agent, dry_run: bool = False) -> list[str]:
    """Move legacy backups from agent install dir to XDG state dir.

    Handles backup-<ts>/ directories (link backups) and *.bak files
    (TOML patch backups) left in the agent install dir by older versions.
    """
    actions: list[str] = []
    xdg_dir = _xdg_backup_dir(agent.key)

    for legacy_dir in sorted(agent.install_path.glob("backup-*")):
        if not legacy_dir.is_dir():
            continue
        dest = xdg_dir / legacy_dir.name
        actions.append(f"MIGRATE {legacy_dir.name} -> {dest}")
        if not dry_run:
            xdg_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(legacy_dir), dest)

    for patch in agent.config_patches:
        target_file = agent.install_path / patch.file
        for bak in sorted(target_file.parent.glob(f"{target_file.name}.*.bak")):
            dest = xdg_dir / bak.name
            actions.append(f"MIGRATE {bak.name} -> {dest}")
            if not dry_run:
                xdg_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(bak), dest)

    return actions


GUARD_SOURCE = "hooks/pre-tool-guard.py"


def status_guard(repo_root: Path, agent: Agent) -> list[tuple[str, str]]:
    """Return the pre-tool guard state (link, registration, python3), or [] if the agent has none."""
    link = next((entry for entry in agent.links if entry.source == GUARD_SOURCE), None)
    if link is None:
        return []
    source, target = _resolve_link(repo_root, agent, link)
    linked = target.is_symlink() and target.resolve() == source

    try:
        settings = json.loads((agent.install_path / "settings.json").read_text())
        entries = settings.get("hooks", {}).get("PreToolUse", [])
    except (OSError, ValueError, AttributeError):
        entries = []
    target_name = Path(link.target).name
    registered = any(
        target_name in hook.get("command", "")
        for entry in entries if isinstance(entry, dict)
        for hook in entry.get("hooks", []) if isinstance(hook, dict)
    )

    python = shutil.which("python3")
    return [
        ("link", "ok" if linked else "not linked (run ai-rules install)"),
        ("registration", "ok" if registered else "not registered in settings.json (run ai-rules update)"),
        ("python3", f"ok ({python})" if python else "not found: the hook cannot run, the permission rules still apply"),
    ]


def status_skill_dirs(repo_root: Path, agent: Agent) -> list[tuple[str, str]]:
    """Return the deployment status of every skill declared for an agent."""
    results: list[tuple[str, str]] = []
    for skill_dir in agent.skill_dirs:
        results.extend(_status_skill_dir(repo_root, agent, skill_dir))
    return results


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

    results.extend(status_skill_dirs(repo_root, agent))

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

    for settings_merge in agent.settings_merges:
        results.append(
            (settings_merge.file, status_settings(repo_root, agent, settings_merge))
        )

    return results
