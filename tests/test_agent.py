from pathlib import Path

import pytest

from ai_rules.agent import Agent, Link, load_agents


SAMPLE_TOML = """
[agents.claude]
name            = "Claude Code"
entry_point     = "agents/claude/CLAUDE.md"
install_dir     = "~/.claude"
supports_imports = true

  [[agents.claude.links]]
  source = "agents/claude/CLAUDE.md"
  target = "CLAUDE.md"

  [[agents.claude.links]]
  source = "rules"
  target = "rules"
"""


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    path = tmp_path / "agents.toml"
    path.write_text(SAMPLE_TOML)
    return path


def test_load_agents_returns_all_agents(config_file: Path) -> None:
    agents = load_agents(config_file)
    assert "claude" in agents


def test_load_agents_parses_agent_fields(config_file: Path) -> None:
    agent = load_agents(config_file)["claude"]
    assert agent.key == "claude"
    assert agent.name == "Claude Code"
    assert agent.entry_point == "agents/claude/CLAUDE.md"
    assert agent.install_dir == "~/.claude"
    assert agent.supports_imports is True


def test_load_agents_parses_links(config_file: Path) -> None:
    agent = load_agents(config_file)["claude"]
    assert len(agent.links) == 2
    assert agent.links[0].source == "agents/claude/CLAUDE.md"
    assert agent.links[0].target == "CLAUDE.md"
    assert agent.links[1].source == "rules"
    assert agent.links[1].target == "rules"


def test_load_agents_defaults_supports_imports_to_false(tmp_path: Path) -> None:
    config = tmp_path / "agents.toml"
    config.write_text("""
[agents.codex]
name = "Codex"
entry_point = "agents/codex/AGENTS.md"
install_dir = "~/.codex"
""")
    agent = load_agents(config)["codex"]
    assert agent.supports_imports is False


def test_agent_install_path_expands_home(config_file: Path) -> None:
    agent = load_agents(config_file)["claude"]
    assert not str(agent.install_path).startswith("~")
    assert agent.install_path == Path.home() / ".claude"


def test_load_agents_empty_file(tmp_path: Path) -> None:
    config = tmp_path / "agents.toml"
    config.write_text("")
    assert load_agents(config) == {}
