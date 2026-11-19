"""Managed JSON merge for agent settings files (Claude Code ``settings.json``).

ai-rules only writes the key paths listed in ``SettingsMerge.owned``. What it
added is recorded in ``$XDG_STATE_HOME/ai-rules/state/<agent>-<stem>.json`` so
that ``update`` can retire dropped entries and ``remove`` reverts exactly what
ai-rules added, leaving keys written by the agent or by the user untouched.
"""

from __future__ import annotations

import json
import os
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_rules.agent import Agent, SettingsMerge

_MISSING = object()

# Entries shipped in the symlinked settings.json up to 0.6.2. A legacy install
# cannot tell them apart from user entries, so migration treats them as owned.
LEGACY_ALLOW = (
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash(npm run *)",
    "Bash(npm install *)",
    "Bash(npm install)",
    "Bash(npx *)",
    "Bash(node *)",
    "Bash(tsc *)",
    "Bash(shellcheck *)",
    "Bash(git init)",
    "Bash(git status)",
    "Bash(git status *)",
    "Bash(git diff)",
    "Bash(git diff *)",
    "Bash(git log)",
    "Bash(git log *)",
    "Bash(git add *)",
    "Bash(git commit *)",
    "Bash(git branch)",
    "Bash(git branch *)",
    "Bash(git checkout *)",
    "Bash(git tag *)",
    "Bash(git push *)",
    "Bash(git stash)",
    "Bash(git stash *)",
    "Bash(ls)",
    "Bash(ls *)",
    "Bash(mkdir *)",
    "Bash(chmod *)",
    "Bash(cp *)",
    "Bash(mv *)",
    "Bash(rm *)",
    "Bash(rmdir *)",
    "Bash(ln -s *)",
    "Bash(cat *)",
    "Bash(echo *)",
    "Bash(which *)",
    "Bash(pwd)",
)
LEGACY_DENY = (
    "Bash(rm -rf *)",
    "Bash(sudo *)",
    "Bash(curl * | bash *)",
    "Bash(wget * | bash *)",
)
LEGACY_SCALARS: dict[str, Any] = {"autoApprove": False}


# --- paths and state ---


def _state_dir() -> Path:
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "ai-rules"


def _state_path(agent: Agent, merge: SettingsMerge) -> Path:
    return _state_dir() / "state" / f"{agent.key}-{Path(merge.file).stem}.json"


def _backup_path(agent: Agent, merge: SettingsMerge) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return _state_dir() / "backups" / agent.key / f"{merge.file}.{timestamp}.bak"


def _empty_state() -> dict[str, Any]:
    return {"version": 1, "added": {}, "scalars": {}}


def _load_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    return state if isinstance(state, dict) else None


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


# --- dotted-path helpers ---


def _get(data: dict[str, Any], path: str) -> Any:
    node: Any = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return _MISSING
        node = node[part]
    return node


def _set(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    node = data
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def _delete(data: dict[str, Any], path: str) -> None:
    """Delete *path*, then prune parent dicts that became empty."""
    parts = path.split(".")
    chain = [data]
    for part in parts[:-1]:
        child = chain[-1].get(part)
        if not isinstance(child, dict):
            return
        chain.append(child)
    chain[-1].pop(parts[-1], None)
    for depth in range(len(parts) - 1, 0, -1):
        if chain[depth]:
            break
        chain[depth - 1].pop(parts[depth - 1], None)


def _set_or_delete(data: dict[str, Any], path: str, entries: list[Any]) -> None:
    if entries:
        _set(data, path, entries)
    else:
        _delete(data, path)


def _owned_values(fragment: dict[str, Any], owned: list[str]) -> dict[str, Any]:
    values = {}
    for path in owned:
        value = _get(fragment, path)
        if value is not _MISSING:
            values[path] = value
    return values


# --- source and target loading ---


def _read_fragment(repo_root: Path, merge: SettingsMerge) -> dict[str, Any] | None:
    try:
        fragment = json.loads((repo_root / merge.source).read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return fragment if isinstance(fragment, dict) else None


def _legacy_state(content: dict[str, Any], desired: dict[str, Any]) -> dict[str, Any]:
    """Build the ownership state of a legacy symlinked install."""
    state = _empty_state()
    owned_lists = {
        "permissions.allow": list(LEGACY_ALLOW),
        "permissions.deny": list(LEGACY_DENY),
    }
    for path, value in desired.items():
        if isinstance(value, list):
            owned_lists[path] = [*owned_lists.get(path, []), *value]
    for path, candidates in owned_lists.items():
        current = _get(content, path)
        if isinstance(current, list):
            added = [entry for entry in current if entry in candidates]
            if added:
                state["added"][path] = added
    for path, value in LEGACY_SCALARS.items():
        if _get(content, path) == value:
            state["scalars"][path] = {"set": value}
    return state


# --- merge ---


def _merge_list(
    content: dict[str, Any], path: str, wanted: list[Any], previously_added: list[Any]
) -> tuple[list[Any], int, int]:
    """Merge *wanted* into the list at *path*; return (added, n_new, n_stale)."""
    current = _get(content, path)
    entries = list(current) if isinstance(current, list) else []
    stale = [e for e in previously_added if e not in wanted and e in entries]
    entries = [e for e in entries if e not in stale]
    new = [e for e in wanted if e not in entries]
    entries.extend(new)
    _set(content, path, entries)
    added = [e for e in wanted if e in new or e in previously_added]
    return added, len(new), len(stale)


def _apply_scalar(
    content: dict[str, Any], path: str, value: Any, record: dict[str, Any] | None
) -> tuple[dict[str, Any] | None, bool]:
    current = _get(content, path)
    if current == value:
        return record, False
    new_record: dict[str, Any] = {"set": value}
    if record is not None and "previous" in record:
        new_record["previous"] = record["previous"]
    elif current is not _MISSING:
        new_record["previous"] = current
    _set(content, path, value)
    return new_record, True


def _retire_scalar(content: dict[str, Any], path: str, record: dict[str, Any]) -> bool:
    if _get(content, path) != record.get("set"):
        return False
    if "previous" in record:
        _set(content, path, record["previous"])
    else:
        _delete(content, path)
    return True


def merge_settings(
    repo_root: Path, agent: Agent, merge: SettingsMerge, dry_run: bool = False
) -> list[str]:
    """Merge the owned keys of the repository fragment into the agent file."""
    target = agent.install_path / merge.file
    fragment = _read_fragment(repo_root, merge)
    if fragment is None:
        return [f"SKIP    {merge.file}: source not found or invalid ({merge.source})"]
    desired = _owned_values(fragment, merge.owned)
    actions: list[str] = []
    state_path = _state_path(agent, merge)
    state = _load_state(state_path) or _empty_state()

    legacy = False
    if target.is_symlink():
        legacy = True
        try:
            content = json.loads(target.resolve(strict=True).read_text())
        except (OSError, json.JSONDecodeError):
            content = {}
        if not isinstance(content, dict):
            content = {}
        state = _legacy_state(content, desired)
        actions.append(f"MIGRATE {merge.file}: symlink replaced by a regular file")
    elif target.exists():
        try:
            content = json.loads(target.read_text())
        except json.JSONDecodeError:
            return [f"SKIP    {merge.file}: parse error, file left untouched"]
        if not isinstance(content, dict):
            return [f"SKIP    {merge.file}: parse error, file left untouched"]
    else:
        content = {}

    original = deepcopy(content)
    new_state = _empty_state()
    n_new = n_stale = 0

    for path, value in desired.items():
        if isinstance(value, list):
            added, new, stale = _merge_list(
                content, path, value, state["added"].get(path, [])
            )
            n_new, n_stale = n_new + new, n_stale + stale
            if added:
                new_state["added"][path] = added
        else:
            record, changed = _apply_scalar(content, path, value, state["scalars"].get(path))
            n_new += changed
            if record is not None:
                new_state["scalars"][path] = record

    # Entries and scalars recorded earlier whose key left the fragment.
    for path, previous in state["added"].items():
        if path not in desired:
            current = _get(content, path)
            if isinstance(current, list):
                kept = [e for e in current if e not in previous]
                n_stale += len(current) - len(kept)
                _set_or_delete(content, path, kept)
    for path, record in state["scalars"].items():
        if path not in desired and _retire_scalar(content, path, record):
            n_stale += 1

    if not legacy and content == original and state == new_state:
        return [f"OK      {merge.file}: already merged"]

    had_file = legacy or (target.exists() and content != original)
    if had_file:
        backup = _backup_path(agent, merge)
        actions.append(f"BACKUP  {merge.file} -> {backup.name}")
        if not dry_run:
            backup.parent.mkdir(parents=True, exist_ok=True)
            if legacy:
                _write_json(backup, content)
            else:
                shutil.copy2(target, backup)

    actions.append(f"MERGE   {merge.file}: +{n_new} added, -{n_stale} retired")
    if not dry_run:
        if legacy:
            target.unlink()
        _write_json(target, content)
        _write_json(state_path, new_state)
    return actions


# --- unmerge ---


def unmerge_settings(
    repo_root: Path, agent: Agent, merge: SettingsMerge, dry_run: bool = False
) -> list[str]:
    """Revert what ai-rules added to the agent file, nothing else."""
    target = agent.install_path / merge.file
    source = (repo_root / merge.source).resolve()

    if target.is_symlink():
        if target.resolve() != source:
            return [f"SKIP    {merge.file}: not managed by ai-rules"]
        if not dry_run:
            target.unlink()
        return [f"UNLINK  {merge.file}: legacy symlink"]

    state_path = _state_path(agent, merge)
    state = _load_state(state_path)
    if state is None or not target.exists():
        return [f"SKIP    {merge.file}: not managed by ai-rules"]
    try:
        content = json.loads(target.read_text())
    except json.JSONDecodeError:
        return [f"SKIP    {merge.file}: parse error, file left untouched"]

    removed = 0
    for path, added in state.get("added", {}).items():
        current = _get(content, path)
        if not isinstance(current, list):
            continue
        kept = [e for e in current if e not in added]
        removed += len(current) - len(kept)
        _set_or_delete(content, path, kept)
    for path, record in state.get("scalars", {}).items():
        removed += _retire_scalar(content, path, record)

    actions = [f"UNMERGE {merge.file}: {removed} entries removed"]
    if not content:
        actions.append(f"DELETE  {merge.file}: empty after removal")
    if not dry_run:
        if content:
            _write_json(target, content)
        else:
            target.unlink()
        state_path.unlink()
    return actions


# --- status ---


def status_settings(repo_root: Path, agent: Agent, merge: SettingsMerge) -> str:
    """Return a one-word or short status for the merged file."""
    target = agent.install_path / merge.file
    if target.is_symlink():
        return "legacy symlink (run update to migrate)"
    if not target.exists():
        return "not installed"
    fragment = _read_fragment(repo_root, merge)
    if fragment is None:
        return "source not found or invalid"
    try:
        content = json.loads(target.read_text())
    except json.JSONDecodeError:
        return "parse error"

    missing = 0
    for path, value in _owned_values(fragment, merge.owned).items():
        current = _get(content, path)
        if isinstance(value, list):
            have = current if isinstance(current, list) else []
            missing += sum(1 for e in value if e not in have)
        elif current != value:
            missing += 1
    return "ok" if missing == 0 else f"patch needed ({missing} missing)"
