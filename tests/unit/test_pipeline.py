import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk import pipeline


def test_ensure_corpus_already_populated():
    core = MagicMock()
    core.get_collection.return_value.count.return_value = 426
    assert pipeline.ensure_corpus(core) == 426


@patch("sdk.pipeline.CorpusIngestor")
def test_ensure_corpus_triggers_ingestion(mock_ingestor_cls):
    core = MagicMock()
    core.get_collection.return_value.count.return_value = 0
    mock_ingestor_cls.return_value.ingest.return_value = 100

    assert pipeline.ensure_corpus(core) == 100
    mock_ingestor_cls.assert_called_once_with(core=core)


@patch("sdk.pipeline.LatexConverter")
def test_run_pipeline_full_flow(mock_converter):
    orchestrator = MagicMock()
    orchestrator.run.return_value = "CREW_RESULT"
    orchestrator.output_path = "data/processed/output.md"
    gate = MagicMock()
    gate.request_approval.return_value = {"approved": True, "decisions": {}}

    with patch("sdk.pipeline.ensure_corpus") as mock_ensure:
        out = pipeline.run_pipeline(orchestrator=orchestrator, gate=gate, skip_ingestion=False)

    mock_ensure.assert_called_once()
    orchestrator.run.assert_called_once()
    # A compile-ready .tex is produced from the raw .md before the gate runs.
    mock_converter.return_value.convert_file.assert_called_once()
    assert str(out["tex_path"]).endswith("output.tex")
    gate.request_approval.assert_called_once_with(out["tex_path"])
    assert out["result"] == "CREW_RESULT"
    assert out["approval"]["approved"] is True
    assert str(out["output_path"]).endswith("output.md")


def test_run_with_retry_recovers_from_transient():
    orchestrator = MagicMock()
    orchestrator.run.side_effect = [Exception("503 UNAVAILABLE"), "OK"]
    sleeps = []
    out = pipeline._run_with_retry(orchestrator, sleep=sleeps.append)
    assert out == "OK"
    assert orchestrator.run.call_count == 2
    assert len(sleeps) == 1


def test_run_with_retry_raises_non_transient():
    orchestrator = MagicMock()
    orchestrator.run.side_effect = Exception("400 invalid request")
    with pytest.raises(Exception, match="400"):
        pipeline._run_with_retry(orchestrator, sleep=lambda _d: None)
    assert orchestrator.run.call_count == 1


def test_run_with_retry_exhausts_retries():
    orchestrator = MagicMock()
    orchestrator.run.side_effect = Exception("503 UNAVAILABLE")
    with pytest.raises(Exception, match="503"):
        pipeline._run_with_retry(orchestrator, retries=3, sleep=lambda _d: None)
    assert orchestrator.run.call_count == 3


@patch("sdk.pipeline.LatexConverter")
def test_run_pipeline_skips_ingestion(mock_converter):
    orchestrator = MagicMock()
    orchestrator.output_path = "out.md"
    gate = MagicMock()
    gate.request_approval.return_value = {"approved": False, "decisions": {}}

    with patch("sdk.pipeline.ensure_corpus") as mock_ensure:
        pipeline.run_pipeline(orchestrator=orchestrator, gate=gate, skip_ingestion=True)

    mock_ensure.assert_not_called()
    mock_converter.return_value.convert_file.assert_called_once()
