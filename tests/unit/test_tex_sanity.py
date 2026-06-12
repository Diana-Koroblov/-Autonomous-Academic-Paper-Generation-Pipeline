import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.tex_sanity import check_tex

GOOD = (
    "\\documentclass{article}\n\\begin{document}\n"
    "Text with math \\[N = R^* \\cdot L\\] and inline $x$.\n"
    "\\begin{itemize}\\item a\\end{itemize}\n"
    "Citation \\cite{ref1}.\n\\printbibliography\n\\end{document}\n"
)


def test_good_tex_passes():
    report = check_tex(GOOD, bib_keys={"ref1"})
    assert report["ok"] is True
    assert report["issues"] == []


def test_unbalanced_inline_math():
    report = check_tex("text $x = 1 more text")
    assert report["ok"] is False
    assert any("inline-math" in i for i in report["issues"])


def test_unbalanced_display_dollars():
    report = check_tex("a $$x$$ b $$y")
    assert any("display-math" in i for i in report["issues"])


def test_unbalanced_brackets_display():
    report = check_tex("open \\[ x = 1 with no close")
    assert any("\\[" in i for i in report["issues"])


def test_unbalanced_braces():
    report = check_tex("\\section{title with no close")
    assert any("braces" in i for i in report["issues"])


def test_mismatched_environments():
    report = check_tex("\\begin{itemize}\\item a\\end{enumerate}")
    assert any("environments" in i for i in report["issues"])


def test_unresolved_cite_keys():
    report = check_tex("\\cite{ref9} and \\cite{ref1}", bib_keys={"ref1"})
    assert report["ok"] is False
    assert any("unresolved cite keys" in i and "ref9" in i for i in report["issues"])


def test_cite_check_skipped_when_no_keys_supplied():
    # Without bib_keys, citation resolution is not evaluated.
    report = check_tex("\\cite{anything}")
    assert report["ok"] is True
