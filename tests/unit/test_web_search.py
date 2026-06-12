import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from tools.web_search import _extract_author, _extract_year, format_web_results, web_search

# ---------------------------------------------------------------------------
# _extract_year
# ---------------------------------------------------------------------------

def test_extract_year_finds_modern_year():
    assert _extract_year("Published in 2023 by MIT Press") == "2023"


def test_extract_year_finds_historical_year():
    assert _extract_year("First described in 1947 near Roswell") == "1947"


def test_extract_year_returns_nd_when_missing():
    assert _extract_year("No date information here") == "n.d."


def test_extract_year_picks_first_match():
    assert _extract_year("From 2001 to 2023") == "2001"


# ---------------------------------------------------------------------------
# _extract_author
# ---------------------------------------------------------------------------

def test_extract_author_single_name():
    assert _extract_author("Smith, J. investigated the phenomenon") == "Smith, J."


def test_extract_author_returns_empty_when_no_match():
    assert _extract_author("no capital pattern here") == ""


def test_extract_author_strips_whitespace():
    result = _extract_author("  Jones, A. wrote the paper")
    assert result == "Jones, A."


# ---------------------------------------------------------------------------
# format_web_results
# ---------------------------------------------------------------------------

def test_format_web_results_empty_returns_no_results_message():
    assert format_web_results([]) == "No web results found."


def test_format_web_results_single_result_contains_fields():
    results = [{"title": "Test Paper", "url": "https://example.com", "snippet": "A snippet", "author": "Smith", "year": "2023"}]
    text = format_web_results(results)
    assert "Test Paper" in text
    assert "https://example.com" in text
    assert "Smith" in text
    assert "2023" in text
    assert "A snippet" in text


def test_format_web_results_unknown_author_shows_placeholder():
    results = [{"title": "T", "url": "u", "snippet": "s", "author": "", "year": "n.d."}]
    text = format_web_results(results)
    assert "(unknown)" in text


def test_format_web_results_truncates_long_snippet():
    long_snippet = "x" * 500
    results = [{"title": "T", "url": "u", "snippet": long_snippet, "author": "", "year": "n.d."}]
    text = format_web_results(results)
    assert "x" * 301 not in text


def test_format_web_results_numbers_results():
    results = [
        {"title": "A", "url": "u1", "snippet": "s1", "author": "", "year": "2020"},
        {"title": "B", "url": "u2", "snippet": "s2", "author": "", "year": "2021"},
    ]
    text = format_web_results(results)
    assert "[Result 1]" in text
    assert "[Result 2]" in text


# ---------------------------------------------------------------------------
# web_search — mocked DDGS
# ---------------------------------------------------------------------------

def _make_ddgs_result(title="Paper", url="https://arxiv.org/abs/1", body="2020 research"):
    return {"title": title, "href": url, "body": body}


def _ddgs_context(mock_ddgs):
    """Returns a mock DDGS class whose instance is mock_ddgs.

    The tool calls ``DDGS().text(...)`` directly (no context manager), so the
    class' return_value — the instance — must carry the mocked ``.text``."""
    mock_cls = MagicMock()
    mock_cls.return_value = mock_ddgs
    return mock_cls


def _patch_ddgs(mock_ddgs_cls):
    """Injects mock_ddgs_cls into sys.modules so the local `from ddgs import DDGS` resolves it."""
    fake_module = MagicMock()
    fake_module.DDGS = mock_ddgs_cls
    return patch.dict("sys.modules", {"ddgs": fake_module})


def test_web_search_returns_structured_results():
    mock_ddgs = MagicMock()
    mock_ddgs.text.return_value = [_make_ddgs_result()]
    mock_cls = _ddgs_context(mock_ddgs)

    with _patch_ddgs(mock_cls):
        results = web_search("extraterrestrials")

    assert len(results) == 1
    assert results[0]["title"] == "Paper"
    assert results[0]["url"] == "https://arxiv.org/abs/1"
    assert results[0]["year"] == "2020"


def test_web_search_falls_back_to_open_query_when_academic_empty():
    mock_ddgs = MagicMock()
    # First call (academic-filtered) returns nothing; second (open) returns one result
    mock_ddgs.text.side_effect = [[], [_make_ddgs_result(title="Fallback")]]
    mock_cls = _ddgs_context(mock_ddgs)

    with _patch_ddgs(mock_cls):
        results = web_search("conspiracy theories")

    assert len(results) == 1
    assert results[0]["title"] == "Fallback"


def test_web_search_returns_empty_on_both_failures():
    mock_ddgs = MagicMock()
    mock_ddgs.text.side_effect = Exception("network error")
    mock_cls = _ddgs_context(mock_ddgs)

    with _patch_ddgs(mock_cls):
        results = web_search("query")

    assert results == []


def test_web_search_academic_success_skips_fallback():
    mock_ddgs = MagicMock()
    mock_ddgs.text.return_value = [_make_ddgs_result(), _make_ddgs_result(title="B")]
    mock_cls = _ddgs_context(mock_ddgs)

    with _patch_ddgs(mock_cls):
        results = web_search("ufo", max_results=2)

    assert len(results) == 2
    assert mock_ddgs.text.call_count == 1  # only the academic call, no fallback


def test_web_search_open_query_exception_returns_empty():
    mock_ddgs = MagicMock()
    # Academic returns nothing, fallback raises
    mock_ddgs.text.side_effect = [[], Exception("timeout")]
    mock_cls = _ddgs_context(mock_ddgs)

    with _patch_ddgs(mock_cls):
        results = web_search("query")

    assert results == []


def test_web_search_import_error_returns_empty():
    # Both the preferred `ddgs` and the legacy `duckduckgo_search` are absent.
    with patch.dict("sys.modules", {"ddgs": None, "duckduckgo_search": None}):
        results = web_search("query")
    assert results == []
