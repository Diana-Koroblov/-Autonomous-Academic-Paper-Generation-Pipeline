import os
import sys

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from agents.writer import WriterAgent


def test_writer_agent_init_success():
    agent = WriterAgent(skill_filename="writing_skill.md")
    assert agent.skill_content is not None
    assert "Writing Skill & Stylistic Protocol" in agent.skill_content


def test_writer_agent_init_skill_not_found():
    with pytest.raises(FileNotFoundError):
        WriterAgent(skill_filename="non_existent_writing_skill_file_random.md")


def test_get_agent():
    agent_wrapper = WriterAgent()
    crew_agent = agent_wrapper.get_agent()

    assert crew_agent.role == "Senior Academic Writer"
    assert "Writing Skill & Stylistic Protocol" in crew_agent.backstory
    assert "Academic Writer" in crew_agent.backstory
