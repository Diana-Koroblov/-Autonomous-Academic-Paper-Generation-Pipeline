import os
import sys

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from agents.latex_agent import LaTeXAgent


def test_latex_agent_init_success():
    agent = LaTeXAgent(skill_filename="latex_skill.md")
    assert agent.skill_content is not None
    assert "LaTeX Production & Compilation Protocol" in agent.skill_content


def test_latex_agent_init_skill_not_found():
    with pytest.raises(FileNotFoundError):
        LaTeXAgent(skill_filename="non_existent_latex_skill_file_random.md")


def test_get_agent():
    agent_wrapper = LaTeXAgent()
    crew_agent = agent_wrapper.get_agent()

    assert crew_agent.role == "Structural LaTeX Typesetter"
    assert "LaTeX Production & Compilation Protocol" in crew_agent.backstory
    assert "LaTeX typesetter" in crew_agent.backstory
