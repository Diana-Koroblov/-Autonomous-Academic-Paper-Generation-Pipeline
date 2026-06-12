import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.md_latex import (
    _is_separator,
    convert_citations,
    escape_text,
    inline,
    md_table,
    placeholder_box,
)


def test_convert_citations_single_and_group():
    assert convert_citations("טקסט [1] ועוד [5, 6, 7].") == "טקסט \\cite{ref1} ועוד \\cite{ref5,ref6,ref7}."


def test_convert_citations_ignores_non_numeric_brackets():
    assert convert_citations("[IMAGE 1: x] [TOC]") == "[IMAGE 1: x] [TOC]"


def test_inline_converts_citation_and_keeps_command():
    out = inline("ראה [3] כאן")
    assert "\\cite{ref3}" in out
    assert "[3]" not in out


def test_escape_text_specials():
    assert escape_text("a & b % c # d _ e") == "a \\& b \\% c \\# d \\_ e"
    assert escape_text("{x}") == "\\{x\\}"


def test_inline_preserves_math():
    assert inline("value $R^*$ here") == "value $R^*$ here"


def test_inline_bold_converted_and_escaped():
    # The 100% inside bold must be escaped while the bold wrapper survives.
    assert inline("**100%**") == "\\textbf{100\\%}"


def test_inline_mixes_math_and_text():
    out = inline("ראה # $x_1$ סוף")
    assert "\\#" in out
    assert "$x_1$" in out


def test_placeholder_box_contains_caption():
    box = placeholder_box("IMAGE 1: pic")
    assert "\\fbox" in box
    assert "IMAGE 1: pic" in box


def test_is_separator():
    assert _is_separator("| :--- | :--- |")
    assert _is_separator("|---|---|")
    assert not _is_separator("| a | b |")


def test_md_table_builds_tabular():
    rows = ["| a | b |", "| :-- | :-- |", "| 1 | 2 |"]
    out = md_table(rows)
    assert out.startswith("\\begin{center}")
    assert "\\begin{tabular}" in out
    assert "a & b \\\\ \\hline" in out
    assert "1 & 2 \\\\ \\hline" in out


def test_md_table_empty_returns_blank():
    assert md_table(["| :-- | :-- |"]) == ""


def test_md_table_pads_short_rows():
    rows = ["| a | b | c |", "| 1 |"]
    out = md_table(rows)
    # Short row padded to 3 columns -> two trailing separators.
    assert "1 &  &  \\\\ \\hline" in out
