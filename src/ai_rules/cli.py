from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from ai_rules import __version__
from ai_rules.agent import load_agents
from ai_rules.config import find_repo_root
from ai_rules.generator import generate_flat_file, verify_flat_file
from ai_rules.installer import install_agent, remove_agent, status_agent

app = typer.Typer(
    name="ai-rules",
    help="Manage shared rules and configuration for AI coding assistants.",
    no_args_is_help=True,
)


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
) -> None:
    pass


def _repo_root() -> Path:
    try:
        return find_repo_root()
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


def _select_agents(repo_root: Path, agent_key: Optional[str]) -> dict:
    agents = load_agents(repo_root / "agents.toml")
    if not agents:
        typer.echo("No agents configured in agents.toml.")
        raise typer.Exit()
    if agent_key:
        if agent_key not in agents:
            available = ", ".join(agents.keys())
            typer.echo(
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
        typer.echo("No agents configured.")
        return

    for key, agent in agents.items():
        imports_label = "native imports" if agent.supports_imports else "generated flat file"
        typer.echo(f"  {key:<14} {agent.name} ({imports_label})")


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
        typer.echo(f"\n[{key}] {ag.name}")
        for name, state in status_agent(repo_root, ag):
            icon = "✓" if state == "ok" else "✗"
            typer.echo(f"  {icon}  {name:<32} {state}")
    typer.echo()


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
        typer.echo("Dry run — no changes will be made.\n")

    for key, ag in agents.items():
        typer.echo(f"[{key}] {ag.name}")
        for action in install_agent(repo_root, ag, dry_run=dry_run):
            typer.echo(f"  {action}")

    typer.echo("\nDone.")


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

    # Find the canonical source: first agent with supports_imports=True
    source_agent = next((a for a in agents.values() if a.supports_imports), None)
    if source_agent is None:
        typer.echo("Error: no agent with supports_imports=True found to use as source.", err=True)
        raise typer.Exit(1)
    source = repo_root / source_agent.entry_point

    targets = _select_agents(repo_root, agent)
    targets = {k: v for k, v in targets.items() if not v.supports_imports}

    if not targets:
        typer.echo("No agents requiring flat file generation.")
        return

    for key, ag in targets.items():
        output = repo_root / ag.entry_point
        if dry_run:
            typer.echo(f"  [dry-run] would generate {output.relative_to(repo_root)}")
        else:
            generate_flat_file(repo_root, source, output, condense=ag.condense_flat_file)
            typer.echo(f"  generated {output.relative_to(repo_root)}")

    if not dry_run:
        typer.echo("\nDone.")


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
        typer.echo("Error: no agent with supports_imports=True found to use as source.", err=True)
        raise typer.Exit(1)
    source = repo_root / source_agent.entry_point

    targets = _select_agents(repo_root, agent)
    targets = {k: v for k, v in targets.items() if not v.supports_imports}

    if not targets:
        typer.echo("No agents requiring flat file verification.")
        return

    all_ok = True
    for key, ag in targets.items():
        output = repo_root / ag.entry_point
        if verify_flat_file(repo_root, source, output, condense=ag.condense_flat_file):
            typer.echo(f"  OK      {output.relative_to(repo_root)}")
        else:
            typer.echo(f"  STALE   {output.relative_to(repo_root)}: run 'ai-rules generate'")
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
        typer.echo("Dry run — no changes will be made.\n")

    for key, ag in agents.items():
        typer.echo(f"[{key}] {ag.name}")
        for action in remove_agent(repo_root, ag, dry_run=dry_run):
            typer.echo(f"  {action}")

    typer.echo("\nDone.")


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
    """Update installation for one or all agents."""
    repo_root = _repo_root()
    agents = _select_agents(repo_root, agent)

    if dry_run:
        typer.echo("Dry run — no changes will be made.\n")

    for key, ag in agents.items():
        typer.echo(f"[{key}] {ag.name}")
        for action in install_agent(repo_root, ag, dry_run=dry_run):
            typer.echo(f"  {action}")

    typer.echo("\nDone.")


if __name__ == "__main__":
    app()
