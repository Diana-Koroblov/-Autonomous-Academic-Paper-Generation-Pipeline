import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from sdk.harness import Harness

@pytest.fixture
def harness():
    return Harness()

def test_session_id(harness):
    assert harness.get_session_id() is not None
    assert isinstance(harness.get_session_id(), str)

def test_token_tracking(harness):
    harness.log_token_usage("researcher", 100, 50)
    harness.log_token_usage("writer", 200, 100)
    
    res_metrics = harness.get_token_metrics("researcher")
    assert res_metrics["input_tokens"] == 100
    assert res_metrics["output_tokens"] == 50
    
    total_metrics = harness.get_token_metrics()
    assert total_metrics["total_input_tokens"] == 300
    assert total_metrics["total_output_tokens"] == 150

def test_log_token_usage_new_agent(harness):
    harness.log_token_usage("unknown_agent", 10, 5)
    metrics = harness.get_token_metrics("unknown_agent")
    assert metrics["input_tokens"] == 10
    assert metrics["output_tokens"] == 5

def test_rag_context_injection_tracking(harness):
    prompt_id = "test_prompt"
    chunks = ["chunk1", "chunk2"]
    metadata = [{"page": 1}, {"page": 2}]
    
    harness.log_rag_context(prompt_id, chunks, metadata)
    log = harness.get_rag_context_log()
    
    assert len(log) == 1
    assert log[0]["prompt_id"] == prompt_id
    assert log[0]["chunks"] == chunks
    assert log[0]["metadata"] == metadata

def test_infrastructure_health_checks(harness):
    health = harness.check_infrastructure_health()
    assert "lualatex_available" in health
    assert "vector_db_reachable" in health
    assert isinstance(health["lualatex_available"], bool)
    assert health["vector_db_reachable"] is True

def test_check_infrastructure_health_exceptions(harness, monkeypatch):
    import shutil
    def mock_which(*args, **kwargs):
        raise Exception("Mocked Exception")
    monkeypatch.setattr(shutil, "which", mock_which)
    
    health = harness.check_infrastructure_health()
    assert health["lualatex_available"] is False
