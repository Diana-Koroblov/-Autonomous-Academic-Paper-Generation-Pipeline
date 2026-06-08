import logging
from pathlib import Path
from typing import Any, Optional

from crewai import Agent

logger = logging.getLogger(__name__)


class WriterAgent:
    """
    Writer Agent specializing in drafting academic Hebrew content.
    Dynamically loads its associated skill and injects it into a CrewAI Agent structure.
    """

    def __init__(
        self,
        llm: Optional[Any] = None,
        skill_filename: str = "writing_skill.md",
    ) -> None:
        self.llm = llm or "gemini/gemini-1.5-flash"
        self.skill_content = self._load_skill(skill_filename)

    def _load_skill(self, filename: str) -> str:
        """
        Dynamically rediscovers, activates, and injects its assigned skill file via pathlib.Path.
        """
        curr = Path(__file__).resolve()
        # Search multiple directories upwards and downwards
        search_paths = [
            curr.parents[2] / "skills" / filename,
            Path.cwd() / "skills" / filename,
            curr.parents[1] / "skills" / filename,
        ]
        for path in search_paths:
            if path.exists():
                logger.info(f"Loaded skill file from {path}")
                return path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Could not find skill file {filename} in directories: {search_paths}")

    def get_agent(self) -> Agent:
        """
        Constructs and returns the configured CrewAI Agent.
        """
        backstory_text = (
            "You are the senior Academic Writer of the Autonomous Academic Paper Generation Crew.\n"
            "Your writing is majestic, formal, highly structured Hebrew prose.\n"
            f"You MUST follow these strict guidelines and constraints:\n\n{self.skill_content}"
        )

        return Agent(
            role="Senior Academic Writer",
            goal="Draft exhaustive, majestic academic Hebrew chapters containing zero conversational filler.",
            backstory=backstory_text,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[],
        )
