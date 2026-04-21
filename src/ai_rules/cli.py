from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer

from ai_rules import __version__
from ai_rules.agent import load_agents
from ai_rules.config import find_repo_root
from ai_rules.generator import generate_flat_file, verify_flat_file
from ai_rules.installer import install_agent, migrate_agent_backups, remove_agent, status_agent

app = typer.Typer(
    name="ai-rules",
    help="Manage shared rules and configuration for AI coding assistants.",
    no_args_is_help=True,
)


class _State:
    verbose: bool = False
    quiet: bool = False
    debug: bool = False
    no_color: bool = False
    no_log: bool = False
    log_file: Path | None = None


_state = _State()


def _setup_file_logging(log_dir_override: Path | None) -> None:
    if _state.no_log:
        _state.log_file = None
        return
    xdg_state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    log_dir = log_dir_override or xdg_state / "ai-rules" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    _state.log_file = log_dir / f"ai-rules-{today}.log"


def _echo(msg: str = "", *, err: bool = False) -> None:
    """Print respecting --quiet; append to log file when enabled."""
    if not _state.quiet or err:
        typer.echo(msg, err=err)
    if _state.log_file is not None:
        with _state.log_file.open("a") as f:
            f.write(msg + "\n")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"ai-rules {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output."),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress non-error output."),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug mode."),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output."),
    ] = False,
    no_log: Annotated[
        bool,
        typer.Option("--no-log", help="Disable file logging."),
    ] = False,
    log_dir: Annotated[
        Optional[Path],
        typer.Option("--log-dir", help="Override the default log directory."),
    ] = None,
) -> None:
    _state.verbose = verbose
    _state.quiet = quiet
    _state.debug = debug
    _state.no_color = no_color or bool(os.environ.get("NO_COLOR"))
    _state.no_log = no_log
    _setup_file_logging(log_dir)


def _repo_root() -> Path:
    try:
        return find_repo_root()
    except FileNotFoundError as exc:
        _echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


def _select_agents(repo_root: Path, agent_key: Optional[str]) -> dict:
    agents = load_agents(repo_root / "agents.toml")
    if not agents:
        _echo("No agents configured in agents.toml.")
        raise typer.Exit()
    if agent_key:
        if agent_key not in agents:
            available = ", ".join(agents.keys())
            _echo(
                f"Error: unknown agent '{agent_key}'. Available: {available}",
                err=True,
            )
            raise typer.Exit(1)
        return {agent_key: agents[agent_key]}
    return agents


@app.command(name="list")
def list_agents() -> None:
    """List available agents."""
    repo_root = _repo_root()
    agents = load_agents(repo_root / "agents.toml")

    if not agents:
        _echo("No agents configured.")
        return

    for key, agent in agents.items():
        imports_label = "native imports" if agent.supports_imports else "generated flat file"
        _echo(f"  {key:<14} {agent.name} ({imports_label})")


@app.command()
def status(
    agent: Annotated[
        Optional[str],
        typer.Argument(help="Agent key (e.g. claude). Defaults to all agents."),
    ] = None,
) -> None:
    """Show installation status for one or all agents."""
    repo_root = _repo_root()
    agents = _select_agents(repo_root, agent)

    for key, ag in agents.items():
        _echo(f"\n[{key}] {ag.name}")
        for name, state in status_agent(repo_root, ag):
            icon = "✓" if state == "ok" else "✗"
            _echo(f"  {icon}  {name:<32} {state}")
    _echo()


@app.command()
def install(
    agent: Annotated[
        Optional[str],
        typer.Argument(help="Agent key (e.g. claude). Defaults to all agents."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Simulate without making any changes."),
    ] = False,
) -> None:
    """Install rules for one or all agents."""
    repo_root = _repo_root()
    agents = _select_agents(repo_root, agent)

    if dry_run:
        _echo("Dry run — no changes will be made.\n")

    for key, ag in agents.items():
        _echo(f"[{key}] {ag.name}")
        for action in install_agent(repo_root, ag, dry_run=dry_run):
            _echo(f"  {action}")

    _echo("\nDone.")


@app.command()
def generate(
    agent: Annotated[
        Optional[str],
        typer.Argument(help="Agent key to generate flat file for. Defaults to all agents without native import support."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Simulate without writing any files."),
    ] = False,
) -> None:
    """Generate flat rule files for agents that do not support native imports."""
    repo_root = _repo_root()
    agents = load_agents(repo_root / "agents.toml")

    source_agent = next((a for a in agents.values() if a.supports_imports), None)
    if source_agent is None:
        _echo("Error: no agent with supports_imports=True found to use as source.", err=True)
        raise typer.Exit(1)
    source = repo_root / source_agent.entry_point

    targets = _select_agents(repo_root, agent)
    targets = {k: v for k, v in targets.items() if not v.supports_imports}

    if not targets:
        _echo("No agents requiring flat file generation.")
        return

    for key, ag in targets.items():
        output = repo_root / ag.entry_point
        if dry_run:
            _echo(f"  [dry-run] would generate {output.relative_to(repo_root)}")
        else:
            generate_flat_file(repo_root, source, output, condense=ag.condense_flat_file)
            _echo(f"  generated {output.relative_to(repo_root)}")

    if not dry_run:
        _echo("\nDone.")


@app.command()
def verify(
    agent: Annotated[
        Optional[str],
        typer.Argument(help="Agent key to verify. Defaults to all agents without native import support."),
    ] = None,
) -> None:
    """Verify flat rule files are in sync with current rules.

    Exits 1 if any flat file is missing or out of date. Use this in CI to
    ensure 'ai-rules generate' was run after modifying rules.
    """
    repo_root = _repo_root()
    agents = load_agents(repo_root / "agents.toml")

    source_agent = next((a for a in agents.values() if a.supports_imports), None)
    if source_agent is None:
        _echo("Error: no agent with supports_imports=True found to use as source.", err=True)
        raise typer.Exit(1)
    source = repo_root / source_agent.entry_point

    targets = _select_agents(repo_root, agent)
    targets = {k: v for k, v in targets.items() if not v.supports_imports}

    if not targets:
        _echo("No agents requiring flat file verification.")
        return

    all_ok = True
    for key, ag in targets.items():
        output = repo_root / ag.entry_point
        if verify_flat_file(repo_root, source, output, condense=ag.condense_flat_file):
            _echo(f"  OK      {output.relative_to(repo_root)}")
        else:
            _echo(f"  STALE   {output.relative_to(repo_root)}: run 'ai-rules generate'")
            all_ok = False

    if not all_ok:
        raise typer.Exit(1)


@app.command()
def remove(
    agent: Annotated[
        Optional[str],
        typer.Argument(help="Agent key (e.g. claude). Defaults to all agents."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Simulate without making any changes."),
    ] = False,
) -> None:
    """Remove rules for one or all agents, restoring original configuration."""
    repo_root = _repo_root()
    agents = _select_agents(repo_root, agent)

    if dry_run:
        _echo("Dry run — no changes will be made.\n")

    for key, ag in agents.items():
        _echo(f"[{key}] {ag.name}")
        for action in remove_agent(repo_root, ag, dry_run=dry_run):
            _echo(f"  {action}")

    _echo("\nDone.")


@app.command()
def update(
    agent: Annotated[
        Optional[str],
        typer.Argument(help="Agent key (e.g. claude). Defaults to all agents."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Simulate without making any changes."),
    ] = False,
) -> None:
    """Update installation and regenerate flat files for one or all agents.

    Combines install and generate: use this after pulling new rules to apply
    all changes in one step. Also migrates legacy backups to the XDG state dir.
    """
    repo_root = _repo_root()
    all_agents = load_agents(repo_root / "agents.toml")
    selected = _select_agents(repo_root, agent)

    source_agent = next((a for a in all_agents.values() if a.supports_imports), None)

    if dry_run:
        _echo("Dry run — no changes will be made.\n")

    for key, ag in selected.items():
        _echo(f"[{key}] {ag.name}")
        for action in migrate_agent_backups(ag, dry_run=dry_run):
            _echo(f"  {action}")
        for action in install_agent(repo_root, ag, dry_run=dry_run):
            _echo(f"  {action}")
        if not ag.supports_imports and source_agent is not None:
            source = repo_root / source_agent.entry_point
            output = repo_root / ag.entry_point
            if dry_run:
                _echo(f"  [dry-run] would regenerate {output.relative_to(repo_root)}")
            else:
                generate_flat_file(repo_root, source, output, condense=ag.condense_flat_file)
                _echo(f"  regenerated {output.relative_to(repo_root)}")

    _echo("\nDone.")


if __name__ == "__main__":
    app()
