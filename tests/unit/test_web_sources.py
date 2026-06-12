import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.web_sources import clear_web_sources, load_web_references, record_web_sources


def _hit(url, title="Paper", author="Smith", year="2020", snippet="s"):
    return {"title": title, "url": url, "author": author, "year": year, "snippet": snippet}


def test_record_creates_file_and_returns_count(tmp_path):
    sink = tmp_path / "web.json"
    n = record_web_sources([_hit("https://a.org/1"), _hit("https://a.org/2")], path=sink)
    assert n == 2
    assert sink.exists()


def test_record_dedupes_by_url(tmp_path):
    sink = tmp_path / "web.json"
    record_web_sources([_hit("https://a.org/1")], path=sink)
    n = record_web_sources([_hit("https://a.org/1"), _hit("https://a.org/3")], path=sink)
    assert n == 2  # the duplicate URL is not stored twice


def test_record_skips_entries_without_url(tmp_path):
    sink = tmp_path / "web.json"
    n = record_web_sources([_hit(""), {"title": "no url"}], path=sink)
    assert n == 0


def test_load_returns_references_with_url(tmp_path):
    sink = tmp_path / "web.json"
    record_web_sources([_hit("https://arxiv.org/abs/1", title="Quantum", author="Doe", year="2021")], path=sink)
    refs = load_web_references(path=sink)
    assert len(refs) == 1
    assert refs[0].url == "https://arxiv.org/abs/1"
    assert refs[0].title == "Quantum"
    assert refs[0].author == "Doe"
    assert refs[0].filename == ""  # web sources carry no corpus filename/page
    assert refs[0].page == ""


def test_load_missing_file_returns_empty(tmp_path):
    assert load_web_references(path=tmp_path / "nope.json") == []


def test_clear_removes_file(tmp_path):
    sink = tmp_path / "web.json"
    record_web_sources([_hit("https://a.org/1")], path=sink)
    assert sink.exists()
    clear_web_sources(path=sink)
    assert not sink.exists()


def test_clear_missing_file_is_noop(tmp_path):
    # Must not raise when there is nothing to clear.
    clear_web_sources(path=tmp_path / "nope.json")


def test_web_reference_renders_url_in_bib(tmp_path):
    # An end-to-end check that a loaded web reference becomes a url-bearing entry.
    from sdk.bib_sync import build_bib

    sink = tmp_path / "web.json"
    record_web_sources([_hit("https://pubmed.ncbi.nlm.nih.gov/123", title="Belief")], path=sink)
    refs = load_web_references(path=sink)
    refs[0].key = "ref1"
    bib = build_bib(refs)
    assert "url    = {https://pubmed.ncbi.nlm.nih.gov/123}" in bib
    assert "Accessed online" in bib
