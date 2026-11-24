from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ConfigValue = int | float | str | bool


@dataclass
class Link:
    source: str
    target: str


@dataclass
class ConfigPatch:
    file: str
    key: str
    value: ConfigValue


@dataclass
class SettingsMerge:
    """A JSON settings file merged key by key instead of linked.

    *source* is the fragment in the repository; *owned* lists the dotted key
    paths ai-rules is allowed to write (every other key belongs to the agent).
    """

    file: str
    source: str
    owned: list[str]


@dataclass
class SkillDir:
    """A directory of skill folders, linked one symlink per skill.

    Each sub-folder of *source* that holds a ``SKILL.md`` is linked to
    ``<install_dir>/<target>/<folder name>``, so skills written by the user
    live next to the ai-rules ones in the same target directory.
    """

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
    config_patches: list[ConfigPatch] = field(default_factory=list)
    settings_merges: list[SettingsMerge] = field(default_factory=list)
    skill_dirs: list[SkillDir] = field(default_factory=list)
    flat_source: str | None = None

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
        config_patches = [
            ConfigPatch(file=p["file"], key=p["key"], value=p["value"])
            for p in agent_data.get("config_patches", [])
        ]
        settings_merges = [
            SettingsMerge(file=m["file"], source=m["source"], owned=list(m["owned"]))
            for m in agent_data.get("settings_merge", [])
        ]
        skill_dirs = [
            SkillDir(source=d["source"], target=d["target"])
            for d in agent_data.get("skill_dirs", [])
        ]
        agents[key] = Agent(
            key=key,
            name=agent_data["name"],
            entry_point=agent_data["entry_point"],
            install_dir=agent_data["install_dir"],
            supports_imports=agent_data.get("supports_imports", False),
            condense_flat_file=agent_data.get("condense_flat_file", False),
            links=links,
            config_patches=config_patches,
            settings_merges=settings_merges,
            skill_dirs=skill_dirs,
            flat_source=agent_data.get("flat_source"),
        )

    return agents
