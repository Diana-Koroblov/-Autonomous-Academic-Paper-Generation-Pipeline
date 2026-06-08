import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from agents.researcher import ResearcherAgent
from sdk.harness import Harness
from tools.rag_query import RAGQuery


@pytest.fixture
def mock_rag_query():
    mq = MagicMock(spec=RAGQuery)
    # Mocking query response
    mq.query.return_value = [
        {
            "text": "Extraterrestrials exist and SETI is finding them.",
            "metadata": {"source_filename": "seti.pdf", "page_number": 4},
            "similarity": 0.85,
        }
    ]
    return mq


@pytest.fixture
def harness_instance():
    return Harness()


def test_researcher_agent_init_success():
    agent = ResearcherAgent(skill_filename="research_skill.md")
    assert agent.skill_content is not None
    assert "Research Skill & Verification Protocol" in agent.skill_content


def test_researcher_agent_init_skill_not_found():
    with pytest.raises(FileNotFoundError):
        ResearcherAgent(skill_filename="non_existent_skill_file_random.md")


@patch("google.genai.Client")
def test_get_embedding_embeddings_success(mock_client_class):
    mock_client = MagicMock()
    # Mock response.embeddings[0].values
    mock_resp = MagicMock()
    mock_val = MagicMock()
    mock_val.values = [0.1] * 768
    mock_resp.embeddings = [mock_val]
    mock_client.models.embed_content.return_value = mock_resp
    mock_client_class.return_value = mock_client

    agent = ResearcherAgent()
    embedding = agent.get_embedding("hello extraterrestrial")
    assert embedding == [0.1] * 768
    mock_client.models.embed_content.assert_called_with(
        model="text-embedding-004", contents="hello extraterrestrial"
    )


@patch("google.genai.Client")
def test_get_embedding_singular_success(mock_client_class):
    mock_client = MagicMock()
    # Mock response.embedding.values
    mock_resp = MagicMock()
    mock_resp.embeddings = []
    mock_resp.embedding = MagicMock()
    mock_resp.embedding.values = [0.2] * 768
    mock_client.models.embed_content.return_value = mock_resp
    mock_client_class.return_value = mock_client

    agent = ResearcherAgent()
    embedding = agent.get_embedding("hello extraterrestrial")
    assert embedding == [0.2] * 768


@patch("google.genai.Client")
def test_get_embedding_failure(mock_client_class):
    mock_client = MagicMock()
    mock_client.models.embed_content.side_effect = Exception("API Key limit reached")
    mock_client_class.return_value = mock_client

    agent = ResearcherAgent()
    embedding = agent.get_embedding("hello")
    assert embedding == []


def test_run_rag_search_no_query_engine():
    agent = ResearcherAgent(rag_query=None)
    results = agent.run_rag_search("test query")
    assert results == []


@patch.object(ResearcherAgent, "get_embedding")
def test_run_rag_search_empty_embedding(mock_get_embedding, mock_rag_query):
    mock_get_embedding.return_value = []
    agent = ResearcherAgent(rag_query=mock_rag_query)
    results = agent.run_rag_search("test query")
    assert results == []


@patch.object(ResearcherAgent, "get_embedding")
def test_run_rag_search_success(mock_get_embedding, mock_rag_query, harness_instance):
    mock_get_embedding.return_value = [0.1] * 768
    agent = ResearcherAgent(rag_query=mock_rag_query, harness=harness_instance)

    results = agent.run_rag_search("UFO sightings Roswell")
    assert len(results) == 1
    assert results[0]["text"] == "Extraterrestrials exist and SETI is finding them."

    # Verify harness logged it
    rag_logs = harness_instance.get_rag_context_log()
    assert len(rag_logs) == 1
    assert "Extraterrestrials exist and SETI is finding them." in rag_logs[0]["chunks"]
    assert rag_logs[0]["metadata"] == [{"source_filename": "seti.pdf", "page_number": 4}]


@patch("google.genai.Client")
def test_get_embedding_empty_response(mock_client_class):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    del mock_resp.embeddings
    del mock_resp.embedding
    mock_client.models.embed_content.return_value = mock_resp
    mock_client_class.return_value = mock_client

    agent = ResearcherAgent()
    embedding = agent.get_embedding("hello")
    assert embedding == []


def test_get_agent(mock_rag_query):
    agent_wrapper = ResearcherAgent(rag_query=mock_rag_query)
    crew_agent = agent_wrapper.get_agent()

    assert crew_agent.role == "Lead Academic Researcher"
    assert "Research Skill & Verification Protocol" in crew_agent.backstory
    assert "Lead Researcher" in crew_agent.backstory

    # Test the dynamic search_tool function
    assert len(crew_agent.tools) == 1
    tool_func = crew_agent.tools[0]

    # Run the tool when it finds results
    with patch.object(ResearcherAgent, "get_embedding", return_value=[0.1] * 768):
        res = tool_func.func("test query")
        assert "Extraterrestrials exist and SETI is finding them" in res

    # Run the tool when RAG returns empty results
    mock_rag_query.query.return_value = []
    with patch.object(ResearcherAgent, "get_embedding", return_value=[0.1] * 768):
        res = tool_func.func("test query")
        assert "No high-similarity chunks found" in res
