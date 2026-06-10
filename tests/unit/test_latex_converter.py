import os
import sys

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.latex_converter import BIDI_PREAMBLE, LatexConverter

RAW = "\n".join(
    [
        "```latex",
        "\\documentclass[12pt]{book}",
        "\\usepackage{polyglossia}",
        "\\usepackage{fontspec}",
        "\\setmainlanguage{hebrew}",
        "\\setotherlanguage{english}",
        "\\setcode{utf8}",
        "\\setmainfont{David CLM}[Script=Hebrew]",
        "\\newfontfamily\\englishfont{Times New Roman}",
        "\\begin{document}",
        "\\tableofcontents*",
        "\\begin{hebrew}",
        "\\section*{כותרת}",
        "This is **important** text.",
        "\\item \\textbf{open bold here**: rest of line",
        "\\end{hebrew}",
        "\\end{document}",
        "```",
    ]
)


def test_fences_removed():
    out = LatexConverter().convert(RAW)
    assert "```" not in out


def test_invalid_commands_removed():
    out = LatexConverter().convert(RAW)
    assert "\\setcode" not in out
    assert "\\usepackage{polyglossia}" not in out
    assert "\\setmainlanguage" not in out
    assert "David CLM" not in out


def test_bidi_preamble_injected_before_document():
    out = LatexConverter().convert(RAW)
    assert "bidi=basic" in out
    assert out.index(BIDI_PREAMBLE.strip().splitlines()[0]) < out.index("\\begin{document}")


def test_hebrew_env_dropped():
    out = LatexConverter().convert(RAW)
    assert "\\begin{hebrew}" not in out
    assert "\\end{hebrew}" not in out


def test_tableofcontents_destarred():
    out = LatexConverter().convert(RAW)
    assert "\\tableofcontents*" not in out
    assert "\\tableofcontents" in out


def test_paired_markdown_bold_converted():
    out = LatexConverter().convert(RAW)
    assert "**important**" not in out
    assert "\\textbf{important}" in out


def test_stray_markdown_bold_becomes_brace():
    out = LatexConverter().convert(RAW)
    # The unpaired '**' that closed an opened \textbf{ must become '}'.
    assert "**" not in out
    assert "\\textbf{open bold here}: rest of line" in out


def test_convert_file_roundtrip(tmp_path):
    src = tmp_path / "raw.md"
    dst = tmp_path / "out.tex"
    src.write_text(RAW, encoding="utf-8")
    result = LatexConverter().convert_file(src, dst)
    assert result == dst
    assert dst.read_text(encoding="utf-8").startswith("\\documentclass")
