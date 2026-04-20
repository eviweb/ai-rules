from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Link:
    source: str
    target: str


@dataclass
class Agent:
    key: str
    name: str
    entry_point: str
    install_dir: str
    supports_imports: bool
    condense_flat_file: bool
    links: list[Link]

    @property
    def install_path(self) -> Path:
        return Path(self.install_dir).expanduser()


def load_agents(config_path: Path) -> dict[str, Agent]:
    """Load and parse agents.toml, returning a dict keyed by agent identifier."""
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    agents: dict[str, Agent] = {}
    for key, agent_data in data.get("agents", {}).items():
        links = [
            Link(source=lnk["source"], target=lnk["target"])
            for lnk in agent_data.get("links", [])
        ]
        agents[key] = Agent(
            key=key,
            name=agent_data["name"],
            entry_point=agent_data["entry_point"],
            install_dir=agent_data["install_dir"],
            supports_imports=agent_data.get("supports_imports", False),
            condense_flat_file=agent_data.get("condense_flat_file", False),
            links=links,
        )

    return agents
