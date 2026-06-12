import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.bib_sync import (
    build_bib,
    in_text_numbers,
    parse_references,
    validate_sync,
    write_bib,
)

MD = "\n".join(
    [
        "## פרק 1",
        "טקסט עם ציטוט [1] ועוד [2, 3].",
        "טבלה מפנה ל [3].",
        "",
        "## רשימת מקורות",
        "",
        "[1] AARO. (2024). *Report on UAP*. DoD. (Referenced as `s41599-025-04799-8.pdf#page=2`).",
        "[2] Wojcik, D. (2021). *UFO Cosmologies*. (Referenced as `s41599-025-04799-8.pdf#page=3`).",
        "[3] Kahneman, D. (2011). *Thinking, Fast and Slow*. (Referenced as `s41599-025-04799-8.pdf#page=3`).",
    ]
)


def test_parse_references_extracts_metadata():
    refs = parse_references(MD)
    assert [r.number for r in refs] == [1, 2, 3]
    first = refs[0]
    assert first.key == "ref1"
    assert first.year == "2024"
    assert first.title == "Report on UAP"
    assert first.filename == "s41599-025-04799-8.pdf"
    assert first.page == "2"


def test_parse_references_none_when_no_section():
    assert parse_references("## פרק 1\nאין כאן מקורות.") == []


def test_in_text_numbers_excludes_reference_list():
    # [1],[2],[3] appear in body; the entries themselves must not be counted twice.
    assert in_text_numbers(MD) == {1, 2, 3}


def test_build_bib_has_rag_metadata():
    bib = build_bib(parse_references(MD))
    assert bib.count("@misc{") == 3
    assert "@misc{ref1," in bib
    assert "RAG source: s41599-025-04799-8.pdf, page 2" in bib


def test_build_bib_empty():
    assert build_bib([]) == ""


def test_build_bib_sanitizes_multi_comma_author():
    # "Ellwood, R. S., & Dean, H" breaks biber unless wrapped as a literal name
    # and the ampersand is neutralized.
    entry = "[6] Ellwood, R. S., & Dean, H. (1999). *UFO Religions*. (Referenced as `a.pdf#page=3`)."
    doc = "טקסט [6].\n\n## רשימת מקורות\n" + entry
    bib = build_bib(parse_references(doc))
    assert "author = {{Ellwood, R. S., and Dean, H}}" in bib
    assert "&" not in bib


def test_build_bib_omits_non_numeric_year():
    doc = "טקסט [7].\n\n## רשימת מקורות\n[7] Anonymous source. (Referenced as `a.pdf#page=3`)."
    bib = build_bib(parse_references(doc))
    assert "year" not in bib  # 'n.d.' must not be emitted as a year field


def test_validate_sync_ok():
    report = validate_sync(MD, parse_references(MD))
    assert report["ok"] is True
    assert report["broken_citations"] == []
    assert report["missing_metadata"] == []
    assert report["cited"] == [1, 2, 3]


def test_validate_sync_detects_broken_citation():
    # Body cites [9] but the reference list only defines [1] -> broken citation.
    doc = "טקסט [9].\n\n## רשימת מקורות\n[1] A. (2020). *T*. (Referenced as `a.pdf#page=1`)."
    report = validate_sync(doc, parse_references(doc))
    assert report["ok"] is False
    assert report["broken_citations"] == [9]


def test_validate_sync_flags_missing_metadata():
    doc = "טקסט [1].\n\n## רשימת מקורות\n[1] Unknown source with no file."
    report = validate_sync(doc, parse_references(doc))
    assert report["ok"] is False
    assert report["missing_metadata"] == [1]


def test_write_bib_roundtrip(tmp_path):
    bib_path = tmp_path / "references.bib"
    refs = write_bib(MD, bib_path)
    assert len(refs) == 3
    assert bib_path.read_text(encoding="utf-8").count("@misc{") == 3
