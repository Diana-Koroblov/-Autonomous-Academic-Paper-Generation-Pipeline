import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from crewai import Agent
from google import genai
from google.genai import types

from tools.rag_query import RAGQuery

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


class ResearcherAgent:
    """
    Researcher Agent specializing in RAG-driven factual extraction from stored PDF literature.
    Dynamically loads its associated skill and injects it into a CrewAI Agent structure.
    """

    def __init__(
        self,
        rag_query: Optional[RAGQuery] = None,
        llm: Optional[Any] = None,
        harness: Optional[Any] = None,
        skill_filename: str = "research_skill.md",
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        max_iter: int = 5,
    ) -> None:
        self.rag_query = rag_query
        self.llm = llm or "gemini/gemini-2.5-flash"
        self.harness = harness
        self.embedding_model = embedding_model
        self.max_iter = max_iter
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

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a 768-dimension embedding using the configured Gemini embedding model.
        """
        try:
            api_key = os.environ.get("GEMINI_API_KEY", "dummy")
            client = genai.Client(api_key=api_key)
            response = client.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSION),
            )
            if hasattr(response, "embeddings") and response.embeddings:
                return response.embeddings[0].values
            elif hasattr(response, "embedding") and response.embedding:
                return response.embedding.values
            return []
        except Exception as e:
            logger.error(f"Error generating embedding for the RAG query: {e}")
            return []

    def run_rag_search(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Executes a RAG query by first embedding the prompt and then querying the index.
        Applies similarity score threshold validation and logging.
        """
        if not self.rag_query:
            logger.warning("RAGQuery dependency is not configured.")
            return []

        embeddings = self.get_embedding(query_text)
        if not embeddings:
            logger.warning("Could not generate embedding for query.")
            return []

        results = self.rag_query.query([embeddings])

        # Integrate with Harness telemetry if available
        if self.harness and results:
            chunks = [r["text"] for r in results]
            metadatas = [r["metadata"] for r in results]
            self.harness.log_rag_context(f"query_{hash(query_text)}", chunks, metadatas)

        return results

    def get_agent(self) -> Agent:
        """
        Constructs and returns the configured CrewAI Agent.
        """
        from crewai.tools import tool

        @tool("run_rag_search")
        def search_tool(query_text: str) -> str:
            """
            Search and retrieve grounding context from the raw document corpus.
            This is the core anti-hallucination tool.
            """
            results = self.run_rag_search(query_text)
            if not results:
                return "No high-similarity chunks found in RAG database."
            return str(results)

        backstory_text = (
            "You are the elite Lead Researcher of the Autonomous Academic Paper Generation Crew.\n"
            "Your decisions are driven strictly by actual RAG source materials.\n"
            f"You MUST follow these strict behavioral dictates:\n\n{self.skill_content}"
        )

        return Agent(
            role="Lead Academic Researcher",
            goal="Identify, verify, and compile rock-solid factual sections with perfect page-level citations.",
            backstory=backstory_text,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            max_iter=self.max_iter,
            tools=[search_tool],
        )
