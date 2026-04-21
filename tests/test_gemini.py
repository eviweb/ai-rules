from pathlib import Path

import pytest

from ai_rules.agent import load_agents
from ai_rules.generator import generate_flat_file


GEMINI_TOML = """
[agents.claude]
name            = "Claude Code"
entry_point     = "agents/claude/CLAUDE.md"
install_dir     = "~/.claude"
supports_imports = true

  [[agents.claude.links]]
  source = "agents/claude/CLAUDE.md"
  target = "CLAUDE.md"

[agents.gemini]
name             = "Gemini"
entry_point      = "agents/gemini/GEMINI.md"
install_dir      = "~/.gemini"
supports_imports = false

  [[agents.gemini.links]]
  source = "agents/gemini/GEMINI.md"
  target = "GEMINI.md"
"""


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    path = tmp_path / "agents.toml"
    path.write_text(GEMINI_TOML)
    return path


def test_gemini_agent_is_loaded(config_file: Path) -> None:
    agents = load_agents(config_file)
    assert "gemini" in agents


def test_gemini_agent_fields(config_file: Path) -> None:
    agent = load_agents(config_file)["gemini"]
    assert agent.key == "gemini"
    assert agent.name == "Gemini"
    assert agent.entry_point == "agents/gemini/GEMINI.md"
    assert agent.install_dir == "~/.gemini"
    assert agent.supports_imports is False


def test_gemini_agent_has_one_link(config_file: Path) -> None:
    agent = load_agents(config_file)["gemini"]
    assert len(agent.links) == 1
    assert agent.links[0].source == "agents/gemini/GEMINI.md"
    assert agent.links[0].target == "GEMINI.md"


def test_gemini_agent_install_path(config_file: Path) -> None:
    agent = load_agents(config_file)["gemini"]
    assert agent.install_path == Path.home() / ".gemini"


def test_gemini_flat_file_is_generated_from_claude_entry_point(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "language.md").write_text("# Language\n\nEnglish only.\n")

    source = tmp_path / "CLAUDE.md"
    source.write_text("@rules/language.md\n")

    output = tmp_path / "agents" / "gemini" / "GEMINI.md"
    generate_flat_file(tmp_path, source, output)

    assert output.exists()
    content = output.read_text()
    assert "# Language" in content
    assert "@rules/language.md" not in content


def test_gemini_flat_file_has_no_import_directives(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "principles.md").write_text("# Principles\n\nKeep it simple.\n")

    source = tmp_path / "CLAUDE.md"
    source.write_text("# Rules\n\n@rules/principles.md\n")

    output = tmp_path / "agents" / "gemini" / "GEMINI.md"
    generate_flat_file(tmp_path, source, output)

    assert "@rules/" not in output.read_text()
