import sys
import os
import pytest
from pathlib import Path
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from tools.rag_parser import RAGParser

@pytest.fixture
def test_pdf_dir(tmp_path):
    """Creates a temporary directory with mock PDFs for testing."""
    dir_path = tmp_path / "data/raw"
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create a mock PDF
    pdf_path = dir_path / "mock_test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    # Insert a long text to test chunking (e.g., 2500 characters)
    long_text = "A" * 2500
    page.insert_textbox(fitz.Rect(0, 0, 500, 800), long_text)
    doc.save(str(pdf_path))
    doc.close()
    
    # Create an empty PDF to test error handling/empty text
    empty_pdf_path = dir_path / "empty.pdf"
    doc2 = fitz.open()
    doc2.new_page()
    doc2.save(str(empty_pdf_path))
    doc2.close()
    
    yield dir_path

def test_chunk_text():
    """Tests the sliding-window chunking logic ensuring strict sizes."""
    parser = RAGParser(chunk_size=1000, chunk_overlap=100)
    text = "A" * 2500
    chunks = parser.chunk_text(text)
    
    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000
    # remaining: 2500 - 1000(1st) + 100(ov) = 1600 left. 2nd chunk takes 1000.
    # remaining: 1600 - 1000(2nd) + 100(ov) = 700 left. 3rd chunk takes 700.
    assert len(chunks[2]) == 700
    assert chunks[0] == "A" * 1000

def test_parse_pdf(test_pdf_dir):
    """Tests that PDF parsing successfully extracts text and assigns required metadata."""
    parser = RAGParser(raw_dir=test_pdf_dir)
    pdf_path = test_pdf_dir / "mock_test.pdf"
    
    parsed_data = parser.parse_pdf(pdf_path)
    assert len(parsed_data) > 0
    assert "text" in parsed_data[0]
    assert "metadata" in parsed_data[0]
    assert parsed_data[0]["metadata"]["source_filename"] == "mock_test.pdf"
    assert parsed_data[0]["metadata"]["page_number"] == 1

def test_process_directory(test_pdf_dir):
    """Tests iteration over the raw directory, combining chunks from multiple files."""
    parser = RAGParser(raw_dir=test_pdf_dir)
    all_chunks = parser.process_directory()
    
    # mock_test.pdf should produce chunks, empty.pdf should produce 0
    assert len(all_chunks) > 0
    filenames = set(chunk["metadata"]["source_filename"] for chunk in all_chunks)
    assert "mock_test.pdf" in filenames
    assert "empty.pdf" not in filenames

def test_empty_text():
    """Tests edge case handling of empty string input for chunking."""
    parser = RAGParser()
    assert parser.chunk_text("") == []

def test_invalid_directory(tmp_path):
    """Tests graceful handling when the raw data directory does not exist."""
    parser = RAGParser(raw_dir=tmp_path / "non_existent")
    assert parser.process_directory() == []
    
def test_invalid_pdf_file():
    """Tests exception handling for corrupt or non-existent PDF files."""
    parser = RAGParser()
    # Trying to parse a non-existent file will trigger the exception block
    result = parser.parse_pdf(Path("non_existent_file.pdf"))
    assert result == []
