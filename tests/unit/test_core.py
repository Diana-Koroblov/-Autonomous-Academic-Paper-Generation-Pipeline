import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.core import PaperOrchestrator
from tools.rag_query import RAGQuery


@pytest.fixture
def mock_rag_query():
    return MagicMock(spec=RAGQuery)


@pytest.fixture
def orchestrator(mock_rag_query, tmp_path):
    out = tmp_path / "out" / "output.md"
    return PaperOrchestrator(rag_query=mock_rag_query, output_path=out)


def test_init_loads_config_and_agents(orchestrator):
    assert orchestrator.config.get("paper_generation", {}).get("language") == "Hebrew"
    assert orchestrator.researcher is not None
    assert orchestrator.writer is not None
    assert orchestrator.reviewer is not None
    assert orchestrator.latex is not None
    assert orchestrator.harness is not None


def test_load_config_failure_returns_defaults(mock_rag_query):
    orch = PaperOrchestrator(config_path="config/__does_not_exist__.json", rag_query=mock_rag_query)
    assert orch.config == {}
    # Defaults must still be supplied by _paper_params.
    params = orch._paper_params()
    assert params["subject"] == "Extraterrestrials and Conspiracy Theories"
    assert params["language"] == "Hebrew"
    assert params["pages_min"] == 25
    assert params["pages_max"] == 30


@patch("sdk.core.RAGQuery")
def test_build_rag_query_uses_config(mock_rq, tmp_path):
    PaperOrchestrator(output_path=tmp_path / "o.md")
    # The default (unmocked-rag) path must build RAGQuery from config values.
    kwargs = mock_rq.call_args.kwargs
    assert kwargs["similarity_threshold"] == 0.6
    assert kwargs["top_k"] == 5


def test_paper_params_from_config(orchestrator):
    params = orchestrator._paper_params()
    assert params["subject"] == "Extraterrestrials and Conspiracy Theories"
    assert params["language"] == "Hebrew"
    assert params["pages_min"] == 25
    assert params["pages_max"] == 30


def test_build_tasks_flow_and_context(orchestrator):
    tasks = orchestrator.build_tasks()
    assert len(tasks) == 4
    research, write, review, structure = tasks

    # Sequential context chaining (the first task declares no upstream context).
    assert research.context not in ([write], [review], [structure])
    assert write.context == [research]
    assert review.context == [write]
    assert structure.context == [review]

    # Each task carries a distinct agent.
    assert research.agent.role == "Lead Academic Researcher"
    assert write.agent.role == "Senior Academic Writer"
    assert review.agent.role == "Senior Academic Reviewer"
    assert structure.agent.role == "Structural LaTeX Typesetter"

    # Mandated structural placeholders are demanded by the final task.
    assert "Drake Equation" in structure.description
    assert "TikZ" in structure.description
    assert "TOC" in structure.description
    assert structure.output_file.endswith("output.md")


def test_build_crew_sequential(orchestrator):
    crew = orchestrator.build_crew()
    assert len(crew.tasks) == 4
    assert len(crew.agents) == 4


def test_run_executes_crew_and_creates_output_dir(orchestrator):
    fake_crew = MagicMock()
    fake_crew.kickoff.return_value = "FINAL_DRAFT"

    with patch.object(orchestrator, "build_crew", return_value=fake_crew) as mock_build:
        result = orchestrator.run()

    assert result == "FINAL_DRAFT"
    mock_build.assert_called_once()
    fake_crew.kickoff.assert_called_once()
    # The output directory must exist after a run.
    assert orchestrator.output_path.parent.exists()
