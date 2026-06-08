import os
import sys

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from agents.reviewer import ReviewerAgent


def test_reviewer_agent_init_success():
    agent = ReviewerAgent(skill_filename="review_skill.md")
    assert agent.skill_content is not None
    assert "Reviewing Skill & Verification Protocol" in agent.skill_content


def test_reviewer_agent_init_skill_not_found():
    with pytest.raises(FileNotFoundError):
        ReviewerAgent(skill_filename="non_existent_review_skill_file_random.md")


def test_get_agent():
    agent_wrapper = ReviewerAgent()
    crew_agent = agent_wrapper.get_agent()

    assert crew_agent.role == "Senior Academic Reviewer"
    assert "Reviewing Skill & Verification Protocol" in crew_agent.backstory
    assert "Academic Reviewer" in crew_agent.backstory
