import re
from typing import List

# Full compilable LuaLaTeX preamble. babel's bidi=basic renders embedded English
# (Latin) runs LTR inside the RTL Hebrew flow; Arial carries Hebrew glyphs.
PREAMBLE = (
    "\\documentclass[12pt,a4paper]{article}\n"
    "\\usepackage[a4paper,margin=2.5cm]{geometry}\n"
    "\\usepackage{fontspec}\n"
    "\\usepackage[bidi=basic]{babel}\n"
    "\\babelprovide[main,import]{hebrew}\n"
    "\\babelprovide[import]{english}\n"
    "\\babelfont{rm}{Arial}\n"
    "\\usepackage{amsmath}\n"
    "\\usepackage{array}\n"
    "\\usepackage{graphicx}\n"
    # The draft may reference figures that were never generated. Fall back to a
    # labelled box for any missing image so a stray \includegraphics filename
    # cannot abort the build.
    "\\makeatletter\n"
    "\\let\\II@includegraphics\\includegraphics\n"
    "\\renewcommand{\\includegraphics}[2][]{%\n"
    "  \\IfFileExists{#2}{\\II@includegraphics[#1]{#2}}{%\n"
    "  \\fbox{\\parbox{0.7\\linewidth}{\\centering\\vspace{1cm}"
    "{\\ttfamily\\detokenize{#2}}\\\\[0.3em](image not found)\\vspace{1cm}}}}}\n"
    "\\makeatother\n"
    # tikz + libraries cover the flowchart diagrams the draft emits inline;
    # pgfplots covers any \begin{axis} data charts a rogue full-document draft
    # emits, and the legacy `arrows` library supplies the `>=stealth` tip those
    # flowcharts request.
    "\\usepackage{tikz}\n"
    "\\usetikzlibrary{positioning,shapes.geometric,arrows.meta,arrows}\n"
    "\\usepackage{pgfplots}\n"
    "\\pgfplotsset{compat=1.18}\n"
    # The draft's diagrams spread nodes wider than the text block (RTL pushes some
    # off the page edge). Scale every picture's coordinates down so far nodes are
    # pulled back in, then cap the result at \\linewidth as a backstop.
    "\\tikzset{every picture/.append style={scale=0.55, transform shape}}\n"
    "\\usepackage{etoolbox}\n"
    "\\usepackage{adjustbox}\n"
    "\\BeforeBeginEnvironment{tikzpicture}{\\begin{adjustbox}{max width=\\linewidth,center}}\n"
    "\\AfterEndEnvironment{tikzpicture}{\\end{adjustbox}}\n"
    "\\usepackage{float}\n"
    "\\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}\n"
    "\\addbibresource{references.bib}\n"
    "\\setlength{\\parskip}{0.5em}\n"
    "\\setlength{\\parindent}{0pt}\n"
    # hyperref (loaded late, per convention) makes biblatex turn every \cite
    # mark like [1] into a clickable link to its bibliography entry; colorlinks
    # renders those marks in blue so they read as links rather than plain text.
    "\\usepackage{hyperref}\n"
    "\\hypersetup{colorlinks=true,citecolor=blue,linkcolor=blue,urlcolor=blue}\n"
    # caption is loaded after hyperref (per its docs) so \captionof works for
    # tables the draft places inside plain center environments.
    "\\usepackage{caption}\n"
    "\\begin{document}\n"
)

POSTAMBLE = "\\end{document}\n"

_ESCAPES = {
    "\\": "\\textbackslash{}",
    "&": "\\&",
    "%": "\\%",
    "#": "\\#",
    "_": "\\_",
    "{": "\\{",
    "}": "\\}",
    "~": "\\textasciitilde{}",
    "^": "\\textasciicircum{}",
}


def escape_text(text: str) -> str:
    """Escapes LaTeX special characters in a plain (non-math) text run."""
    out = []
    for ch in text:
        out.append(_ESCAPES.get(ch, ch))
    return "".join(out)


def _bold_and_escape(text: str) -> str:
    """Converts Markdown **bold** to \\textbf{} and escapes the surrounding text."""
    segments = re.split(r"\*\*(.+?)\*\*", text)
    rendered = []
    for idx, seg in enumerate(segments):
        escaped = escape_text(seg)
        rendered.append(f"\\textbf{{{escaped}}}" if idx % 2 == 1 else escaped)
    return "".join(rendered)


_CITATION_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")

# Maximum unique bibliography entries. Any citation number above this is
# round-robin mapped to 1..MAX_CITE so no \cite key is ever left undefined.
MAX_CITE = 20


def _remap_cite(n: int) -> int:
    return n if n <= MAX_CITE else ((n - 1) % MAX_CITE) + 1


def convert_citations(text: str) -> str:
    """Maps numeric in-text citations like [5, 6] to \\cite{ref5,ref6}.

    Numbers above MAX_CITE are remapped round-robin so every key resolves
    to one of the capped bibliography entries."""

    def repl(match: "re.Match[str]") -> str:
        seen: set[str] = set()
        keys = []
        for n in match.group(1).split(","):
            key = f"ref{_remap_cite(int(n.strip()))}"
            if key not in seen:
                keys.append(key)
                seen.add(key)
        return f"\\cite{{{','.join(keys)}}}"

    return _CITATION_RE.sub(repl, text)


def inline(text: str) -> str:
    """
    Renders an inline Markdown run to LaTeX: numeric citations become \\cite,
    inline math ($...$) and the emitted \\cite{...} are preserved verbatim, and
    the remaining text is escaped with **bold** converted.
    """
    text = convert_citations(text)
    # Preserve inline math, \cite, and the common formatting macros a draft may
    # emit inline (e.g. after a \RTL{...} wrapper is unwrapped); escape the rest.
    parts = re.split(r"(\$[^$]*\$|\\(?:cite|textbf|textit|emph|texttt|underline)\{[^}]*\})", text)
    out = []
    for part in parts:
        is_math = len(part) >= 2 and part.startswith("$") and part.endswith("$")
        if is_math or part.startswith("\\"):
            out.append(part)
        else:
            out.append(_bold_and_escape(part))
    return "".join(out)


def figure_block(path: str, caption: str) -> str:
    return (
        "\\begin{figure}[H]\n\\centering\n"
        f"\\includegraphics[width=0.8\\linewidth]{{{path}}}\n"
        f"\\caption{{{escape_text(caption)}}}\n"
        "\\end{figure}"
    )


def title_block(text: str) -> str:
    return "\\begin{center}\n{\\Huge " + inline(text) + "}\n\\end{center}\n\\vspace{1em}"


def placeholder_box(caption: str) -> str:
    """
    A framed box standing in for a missing asset (image/graph/diagram). The
    caption is set upright (not italic): Arial's italic instance lacks Hebrew
    glyphs on some systems, which would silently drop the characters.
    """
    return (
        "\\begin{center}\n\\fbox{\\begin{minipage}{0.85\\linewidth}\n"
        f"\\centering {escape_text(caption)}\n"
        "\\end{minipage}}\n\\end{center}"
    )


def _is_separator(row: str) -> bool:
    """True for a Markdown table separator row like | :--- | :--- |."""
    return bool(re.fullmatch(r"\|[\s:\-\|]+\|", row.strip()))


def md_table(rows: List[str]) -> str:
    """Converts a collected Markdown table (pipe rows) to a LaTeX tabular."""
    cells = [
        [c.strip() for c in row.strip().strip("|").split("|")]
        for row in rows
        if row.strip().startswith("|") and not _is_separator(row)
    ]
    if not cells:
        return ""
    ncols = max(len(r) for r in cells)
    width = 0.9 / ncols
    colspec = "|" + "|".join([f"p{{{width:.2f}\\linewidth}}"] * ncols) + "|"
    lines = ["\\begin{center}", f"\\begin{{tabular}}{{{colspec}}}", "\\hline"]
    for row in cells:
        padded = row + [""] * (ncols - len(row))
        lines.append(" & ".join(inline(c) for c in padded) + " \\\\ \\hline")
    lines += ["\\end{tabular}", "\\end{center}"]
    return "\n".join(lines)
