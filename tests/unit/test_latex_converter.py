import os
import sys

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.latex_converter import LatexConverter

RAW = "\n".join(
    [
        "**כותרת ראשית**",
        "",
        "## פרק 1: מבוא",
        "",
        "[TOC]",
        "",
        "### 1.1 רקע",
        "",
        "טקסט עם **הדגשה** ומתמטיקה $N$ בתוך השורה.",
        "",
        "[IMAGE 1: תרשים]",
        "",
        "* פריט ראשון",
        "* פריט שני",
        "",
        "1. שלב אחד",
        "2. שלב שתיים",
        "",
        "[DRAKE EQUATION]",
        "$$N = R^* \\cdot f_p$$",
        "",
        "[TABLE 1]",
        "| א | ב |",
        "| :-- | :-- |",
        "| 1 | 2 |",
        "",
        "מקור עם תו מיוחד #page=2 בטקסט.",
    ]
)


def test_document_is_wrapped():
    out = LatexConverter().convert(RAW)
    assert out.startswith("\\documentclass")
    assert out.rstrip().endswith("\\end{document}")
    assert "bidi=basic" in out


def test_title_rendered_once():
    out = LatexConverter().convert(RAW)
    assert "\\Huge \\textbf{כותרת ראשית}" in out


def test_headings_mapped():
    out = LatexConverter().convert(RAW)
    assert "\\section{פרק 1: מבוא}" in out
    assert "\\subsection{1.1 רקע}" in out


def test_toc_marker_becomes_tableofcontents():
    out = LatexConverter().convert(RAW)
    assert "\\tableofcontents" in out
    assert "[TOC]" not in out


def test_inline_bold_and_math_preserved():
    out = LatexConverter().convert(RAW)
    assert "\\textbf{הדגשה}" in out
    assert "$N$" in out  # inline math kept verbatim


def test_lists_rendered():
    out = LatexConverter().convert(RAW)
    assert "\\begin{itemize}" in out and "\\end{itemize}" in out
    assert "\\begin{enumerate}" in out and "\\end{enumerate}" in out
    assert out.count("\\item") == 4


def test_display_equation_rendered():
    out = LatexConverter().convert(RAW)
    assert "\\[N = R^* \\cdot f_p\\]" in out
    assert "[DRAKE EQUATION]" not in out
    assert "$$" not in out


def test_asset_placeholder_boxed():
    out = LatexConverter().convert(RAW)
    assert "\\fbox" in out
    assert "IMAGE 1: תרשים" in out


def test_markdown_table_to_tabular():
    out = LatexConverter().convert(RAW)
    assert "\\begin{tabular}" in out
    assert "[TABLE 1]" not in out
    assert ":--" not in out  # separator row consumed, not emitted


def test_special_char_escaped_outside_math():
    out = LatexConverter().convert(RAW)
    assert "\\#page=2" in out


CITED = "\n".join(
    [
        "## פרק 1",
        "",
        "טענה ראשונה [1] ושנייה [2, 3].",
        "",
        "## רשימת מקורות",
        "",
        "[1] AARO. (2024). *Report*. (Referenced as `a.pdf#page=2`).",
        "[2] Wojcik. (2021). *UFO*. (Referenced as `a.pdf#page=3`).",
        "[3] Kahneman. (2011). *Thinking*. (Referenced as `a.pdf#page=3`).",
    ]
)


def test_body_citations_become_cite():
    out = LatexConverter().convert(CITED)
    assert "\\cite{ref1}" in out
    assert "\\cite{ref2,ref3}" in out


def test_references_section_becomes_printbibliography():
    out = LatexConverter().convert(CITED)
    assert "\\printbibliography" in out
    # The raw reference entries are dropped (now living in references.bib).
    assert "Referenced as" not in out
    assert "\\section{רשימת מקורות}" not in out


def test_nocite_seeds_numbering_in_order():
    out = LatexConverter().convert(CITED)
    assert "\\nocite{ref1,ref2,ref3}" in out


def test_addbibresource_in_preamble():
    out = LatexConverter().convert(CITED)
    assert "\\addbibresource{references.bib}" in out


def test_convert_file_roundtrip(tmp_path):
    src = tmp_path / "raw.md"
    dst = tmp_path / "out.tex"
    src.write_text(RAW, encoding="utf-8")
    result = LatexConverter().convert_file(src, dst)
    assert result == dst
    assert dst.read_text(encoding="utf-8").startswith("\\documentclass")
