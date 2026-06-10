import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from crewai import Crew, Process, Task

from agents.latex_agent import LaTeXAgent
from agents.researcher import ResearcherAgent
from agents.reviewer import ReviewerAgent
from agents.writer import WriterAgent
from sdk.harness import Harness
from tools.rag_query import RAGQuery

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config/setup.json"
DEFAULT_OUTPUT_PATH = "data/processed/output.md"


class PaperOrchestrator:
    """
    SDK Core orchestrator coordinating the CrewAI team (Researcher, Writer,
    Reviewer, LaTeX) and the sequential task execution flow that produces the
    structured Hebrew academic Markdown draft.
    """

    def __init__(
        self,
        config_path: str | Path = DEFAULT_CONFIG_PATH,
        rag_query: Optional[RAGQuery] = None,
        harness: Optional[Harness] = None,
        output_path: str | Path = DEFAULT_OUTPUT_PATH,
    ) -> None:
        self.config = self._load_config(config_path)
        self.harness = harness or Harness()
        self.output_path = Path(output_path)
        self.rag_query = rag_query or self._build_rag_query()
        models = self.config.get("models", {})
        draft_llm = f"gemini/{models.get('drafting', 'gemini-2.5-flash')}"
        review_llm = f"gemini/{models.get('reviewing', 'gemini-2.5-pro')}"
        embed_model = models.get("embedding", "gemini-embedding-001")
        self.researcher = ResearcherAgent(
            rag_query=self.rag_query, harness=self.harness, llm=draft_llm, embedding_model=embed_model
        )
        self.writer = WriterAgent(llm=draft_llm)
        self.reviewer = ReviewerAgent(llm=review_llm)
        self.latex = LaTeXAgent(llm=draft_llm)

    def _build_rag_query(self) -> RAGQuery:
        rag = self.config.get("rag_engine", {})
        return RAGQuery(
            similarity_threshold=rag.get("similarity_threshold", 0.6),
            top_k=rag.get("top_k_retrieval", 5),
        )

    def _load_config(self, path: str | Path) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config {path}: {e}. Using defaults.")
            return {}

    def _paper_params(self) -> Dict[str, Any]:
        params = self.config.get("paper_generation", {})
        return {
            "subject": params.get("subject", "Extraterrestrials and Conspiracy Theories"),
            "language": params.get("language", "Hebrew"),
            "pages_min": params.get("target_pages_min", 25),
            "pages_max": params.get("target_pages_max", 30),
        }

    def build_tasks(self) -> List[Task]:
        """Constructs the ordered Research -> Write -> Review -> Structure task flow."""
        p = self._paper_params()
        research = Task(
            description=(
                f"Extract verifiable, citation-backed facts about '{p['subject']}' using the RAG "
                "search tool. Reject any claim that is not grounded in the retrieved source chunks."
            ),
            expected_output="A structured list of facts, each tagged with its source filename and page number.",
            agent=self.researcher.get_agent(),
        )
        write = Task(
            description=(
                f"Draft a {p['pages_min']}-{p['pages_max']} page academic paper in {p['language']} "
                f"about '{p['subject']}', using ONLY the verified research facts as grounding."
            ),
            expected_output=f"A complete academic {p['language']} draft in Markdown with chapters and sections.",
            agent=self.writer.get_agent(),
            context=[research],
        )
        review = Task(
            description=(
                "Audit the draft for academic tone, structural coherence, and zero hallucinations. "
                "Every factual claim must trace back to a research citation."
            ),
            expected_output="The corrected, fully verified academic draft with all citations preserved.",
            agent=self.reviewer.get_agent(),
            context=[write],
        )
        structure = Task(
            description=(
                "Inject strict structural placeholders into the verified draft: an automatic TOC, "
                "chapter and header/footer markers, and tags for at least one image, one data graph, "
                "one summary table, one complex TikZ block diagram, and the mathematical Drake Equation."
            ),
            expected_output="The final structured Markdown draft containing all mandated placeholders.",
            agent=self.latex.get_agent(),
            context=[review],
            output_file=str(self.output_path),
        )
        return [research, write, review, structure]

    def build_crew(self) -> Crew:
        """Assembles the sequential CrewAI crew from the configured agents and tasks."""
        tasks = self.build_tasks()
        agents = [task.agent for task in tasks]
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    def run(self) -> Any:
        """Executes the full pipeline and returns the CrewAI result object."""
        session_id = self.harness.get_session_id()
        logger.info("Starting paper generation pipeline.", extra={"session_id": session_id})
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        result = self.build_crew().kickoff()
        logger.info("Pipeline execution finished.", extra={"session_id": session_id})
        return result
