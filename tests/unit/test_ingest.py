import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.ingest import CorpusIngestor


@pytest.fixture
def chunks():
    return [
        {"text": "alpha", "metadata": {"source_filename": "a.pdf", "page_number": 1}},
        {"text": "beta", "metadata": {"source_filename": "a.pdf", "page_number": 2}},
        {"text": "gamma", "metadata": {"source_filename": "b.pdf", "page_number": 1}},
    ]


@pytest.fixture
def ingestor(chunks):
    parser = MagicMock()
    parser.process_directory.return_value = chunks
    core = MagicMock()
    return CorpusIngestor(parser=parser, core=core, batch_size=2)


def _embed_response(n):
    resp = MagicMock()
    resp.embeddings = [MagicMock(values=[0.1] * 768) for _ in range(n)]
    return resp


def test_build_id(ingestor, chunks):
    assert ingestor._build_id(chunks[0], 0) == "a.pdf_p1_0"
    assert ingestor._build_id(chunks[2], 2) == "b.pdf_p1_2"


def test_embed_batch_empty(ingestor):
    assert ingestor.embed_batch([]) == []


@patch("google.genai.Client")
def test_embed_batch_calls_model(mock_client_class, ingestor):
    mock_client = MagicMock()
    mock_client.models.embed_content.return_value = _embed_response(2)
    mock_client_class.return_value = mock_client

    out = ingestor.embed_batch(["x", "y"])
    assert len(out) == 2 and len(out[0]) == 768
    call = mock_client.models.embed_content.call_args
    assert call.kwargs["model"] == "gemini-embedding-001"
    assert call.kwargs["config"].output_dimensionality == 768


def test_ingest_empty_corpus():
    parser = MagicMock()
    parser.process_directory.return_value = []
    ing = CorpusIngestor(parser=parser, core=MagicMock())
    assert ing.ingest() == 0


@patch.object(CorpusIngestor, "embed_batch")
def test_ingest_batches_and_persists(mock_embed, ingestor):
    # batch_size=2 over 3 chunks -> batches of 2 and 1
    mock_embed.side_effect = [[[0.1] * 768] * 2, [[0.1] * 768] * 1]
    inserted = ingestor.ingest()

    assert inserted == 3
    assert ingestor.core.insert_vectors.call_count == 2
    first_ids = ingestor.core.insert_vectors.call_args_list[0].args[0]
    assert first_ids == ["a.pdf_p1_0", "a.pdf_p2_1"]


@patch.object(CorpusIngestor, "embed_batch")
def test_ingest_skips_empty_embeddings(mock_embed, ingestor):
    mock_embed.return_value = []
    assert ingestor.ingest() == 0
    ingestor.core.insert_vectors.assert_not_called()


@patch("sdk.ingest.time.sleep", return_value=None)
@patch("google.genai.Client")
def test_embed_batch_retries_on_429(mock_client_class, mock_sleep, ingestor):
    mock_client = MagicMock()
    mock_client.models.embed_content.side_effect = [Exception("429 RESOURCE_EXHAUSTED"), _embed_response(1)]
    mock_client_class.return_value = mock_client

    out = ingestor.embed_batch(["x"])
    assert len(out) == 1
    assert mock_client.models.embed_content.call_count == 2
    mock_sleep.assert_called_once()


@patch("sdk.ingest.time.sleep", return_value=None)
@patch("google.genai.Client")
def test_embed_batch_raises_non_429(mock_client_class, mock_sleep, ingestor):
    mock_client = MagicMock()
    mock_client.models.embed_content.side_effect = Exception("500 boom")
    mock_client_class.return_value = mock_client

    with pytest.raises(Exception, match="500"):
        ingestor.embed_batch(["x"])
