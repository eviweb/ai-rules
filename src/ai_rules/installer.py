from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from ai_rules.agent import Agent, Link


def _backup_dir(install_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return install_path / f"backup-{timestamp}"


def _resolve_link(repo_root: Path, agent: Agent, link: Link) -> tuple[Path, Path]:
    source = (repo_root / link.source).resolve()
    target = agent.install_path / link.target
    return source, target


def install_agent(
    repo_root: Path, agent: Agent, dry_run: bool = False
) -> list[str]:
    """Deploy symlinks for an agent. Returns a list of human-readable action lines."""
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

    return actions


def status_agent(repo_root: Path, agent: Agent) -> list[tuple[str, str]]:
    """Return the installation status of each declared link for an agent."""
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

    return results
