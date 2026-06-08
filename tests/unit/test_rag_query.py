import sys
import os
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from tools.rag_query import RAGQuery

# Mock classes to simulate ChromaDB behavior without a real database connection
class MockCollection:
    def __init__(self, mock_results):
        self.mock_results = mock_results
        
    def query(self, query_embeddings, n_results, include):
        return self.mock_results

class MockCore:
    def __init__(self, mock_results):
        self.collection = MockCollection(mock_results)
        
    def get_collection(self):
        return self.collection

@pytest.fixture
def empty_mock_core():
    # Simulate empty DB
    results = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    return MockCore(results)

@pytest.fixture
def mock_core():
    # Simulate results with varying distances (1 - cosine_similarity)
    # Target similarity threshold is >= 0.72.
    # Distances corresponding to similarities:
    # 0.9 similarity -> 0.1 distance (Pass)
    # 0.72 similarity -> 0.28 distance (Pass)
    # 0.7 similarity -> 0.3 distance (Fail)
    # 0.6 similarity -> 0.4 distance (Fail)
    results = {
        "documents": [["Doc 1", "Doc 2", "Doc 3", "Doc 4"]],
        "metadatas": [[{"page": 1}, {"page": 2}, {"page": 3}, {"page": 4}]],
        "distances": [[0.1, 0.28, 0.3, 0.4]]
    }
    return MockCore(results)

def test_query_empty_input():
    query_engine = RAGQuery()
    assert query_engine.query([]) == []

def test_query_anti_hallucination_gate(mock_core):
    """
    Tests that only results with a similarity score >= 0.72 are returned.
    """
    query_engine = RAGQuery(core_instance=mock_core, similarity_threshold=0.72)
    # Dummy embedding input
    embeddings = [[0.1] * 768]
    
    results = query_engine.query(embeddings)
    
    # Should only return the first two docs (scores 0.9 and 0.72)
    assert len(results) == 2
    assert results[0]["text"] == "Doc 1"
    assert results[0]["similarity"] == 0.9
    assert results[1]["text"] == "Doc 2"
    
    # Due to floating point math, 1 - 0.28 might be 0.7200000000000001
    assert pytest.approx(results[1]["similarity"], 0.001) == 0.72

def test_query_all_rejected(mock_core):
    """
    Tests that if the threshold is raised so no docs pass, it returns an empty list.
    """
    query_engine = RAGQuery(core_instance=mock_core, similarity_threshold=0.95)
    embeddings = [[0.1] * 768]
    
    results = query_engine.query(embeddings)
    assert len(results) == 0

def test_query_empty_collection(empty_mock_core):
    """
    Tests behavior when the collection returns no results.
    """
    query_engine = RAGQuery(core_instance=empty_mock_core)
    embeddings = [[0.1] * 768]
    
    results = query_engine.query(embeddings)
    assert len(results) == 0

def test_query_exception_handling():
    """
    Tests that database exceptions are caught and an empty list is returned.
    """
    class ErrorCollection:
        def query(self, *args, **kwargs):
            raise Exception("Database Connection Error")
            
    class ErrorCore:
        def get_collection(self):
            return ErrorCollection()
            
    query_engine = RAGQuery(core_instance=ErrorCore())
    embeddings = [[0.1] * 768]
    
    results = query_engine.query(embeddings)
    assert len(results) == 0
