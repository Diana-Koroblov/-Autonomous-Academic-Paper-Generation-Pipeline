import sys
import os
import pytest
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from tools.rag_core import RAGCore

@pytest.fixture
def test_persist_dir(tmp_path):
    """Provides a temporary directory for ChromaDB persistence during tests."""
    test_dir = tmp_path / "test_chroma_db"
    yield str(test_dir)
    # Cleanup after test
    if test_dir.exists():
        shutil.rmtree(test_dir, ignore_errors=True)

@pytest.fixture
def rag_core(test_persist_dir):
    """Initializes a fresh RAGCore instance for testing."""
    return RAGCore(persist_directory=test_dir)

def test_rag_core_initialization(test_persist_dir):
    """Tests if RAGCore initializes and creates the persistence directory."""
    core = RAGCore(persist_directory=test_persist_dir)
    assert os.path.exists(test_persist_dir)
    assert core.collection_name == "academic_corpus"
    assert core.embedding_dimension == 768

def test_get_collection(test_persist_dir):
    """Tests if the collection is successfully retrieved or created with correct metadata."""
    core = RAGCore(persist_directory=test_persist_dir)
    collection = core.get_collection()
    assert collection is not None
    assert collection.name == "academic_corpus"

def test_insert_vectors_success(test_persist_dir):
    """Tests successful insertion of valid 768-dimensional vectors."""
    core = RAGCore(persist_directory=test_persist_dir)
    
    # Mock data
    ids = ["doc1", "doc2"]
    # 768 dimensions for text-embedding-004
    embeddings = [[0.1] * 768, [0.2] * 768]
    documents = ["Content of doc1", "Content of doc2"]
    metadatas = [{"source_filename": "test.pdf", "page_number": 1}, {"source_filename": "test.pdf", "page_number": 2}]
    
    # Execute insertion
    core.insert_vectors(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    
    # Verify insertion
    collection = core.get_collection()
    results = collection.get(ids=["doc1", "doc2"])
    
    assert len(results["ids"]) == 2
    assert "doc1" in results["ids"]
    assert results["documents"] == documents

def test_insert_vectors_dimension_mismatch(test_persist_dir):
    """Tests that insertion fails if dimensions do not equal 768."""
    core = RAGCore(persist_directory=test_persist_dir)
    
    ids = ["doc_invalid"]
    # Invalid dimension (e.g., 512)
    embeddings = [[0.1] * 512]
    documents = ["Invalid dimension content"]
    metadatas = [{"source": "invalid"}]
    
    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        core.insert_vectors(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

def test_insert_empty_vectors(test_persist_dir):
    """Tests that empty insertions return gracefully."""
    core = RAGCore(persist_directory=test_persist_dir)
    # Should not raise any errors
    core.insert_vectors(ids=[], embeddings=[], documents=[], metadatas=[])
