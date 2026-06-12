import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk import post_generation

MD = "\n".join(
    [
        "טקסט עם [1].",
        "",
        "## רשימת מקורות",
        "[1] AARO. (2024). *Report*. (Referenced as `a.pdf#page=2`).",
    ]
)


def test_synchronize_bibliography_writes_bib_and_reports(tmp_path):
    md_path = tmp_path / "output.md"
    md_path.write_text(MD, encoding="utf-8")
    tex_path = tmp_path / "output.tex"
    tex_path.write_text("\\cite{ref1}\n\\printbibliography", encoding="utf-8")

    report = post_generation.synchronize_bibliography(md_path, tex_path)

    assert (tmp_path / "references.bib").exists()
    assert report["entries"] == 1
    assert report["sync"]["ok"] is True
    assert report["sanity"]["ok"] is True


def test_synchronize_bibliography_flags_unresolved_cite(tmp_path):
    md_path = tmp_path / "output.md"
    md_path.write_text(MD, encoding="utf-8")
    tex_path = tmp_path / "output.tex"
    # Body cites ref9, which the draft never listed. With no corpus to fall back
    # on, it stays unresolved -> Gate 4 sanity must fail.
    tex_path.write_text("\\cite{ref9}", encoding="utf-8")
    empty_corpus = tmp_path / "empty_corpus"
    empty_corpus.mkdir()

    report = post_generation.synchronize_bibliography(md_path, tex_path, corpus_dir=empty_corpus)
    assert report["sanity"]["ok"] is False


def test_synchronize_bibliography_grounds_unlisted_cite_in_corpus(tmp_path):
    # A draft with no reference list at all: every \cite must still resolve by
    # falling back to a real corpus document, so Gate 4 sanity passes.
    md_path = tmp_path / "output.md"
    md_path.write_text("טקסט עם [1] ו[2].", encoding="utf-8")
    tex_path = tmp_path / "output.tex"
    tex_path.write_text("\\cite{ref1}\n\\cite{ref2}\n\\printbibliography", encoding="utf-8")

    report = post_generation.synchronize_bibliography(md_path, tex_path)

    assert report["entries"] == 2
    assert report["sanity"]["ok"] is True


@patch("sdk.post_generation.LatexCompiler")
def test_verify_length_reads_config_target(mock_compiler, tmp_path):
    orchestrator = MagicMock()
    orchestrator.config = {"paper_generation": {"verify_pages_min": 14, "verify_pages_max": 16}}
    mock_compiler.return_value.verify.return_value = {"status": "PASS", "page_count": 16}

    post_generation.verify_length(orchestrator, tmp_path / "output.tex")

    args, _ = mock_compiler.return_value.verify.call_args
    assert args[1] == 14 and args[2] == 16


@patch("sdk.post_generation.LatexCompiler")
def test_verify_length_defaults_when_config_missing(mock_compiler, tmp_path):
    orchestrator = MagicMock()
    orchestrator.config = {}
    mock_compiler.return_value.verify.return_value = {"status": "PASS", "page_count": 15}

    post_generation.verify_length(orchestrator, tmp_path / "output.tex")

    args, _ = mock_compiler.return_value.verify.call_args
    assert args[1] == 14 and args[2] == 16
