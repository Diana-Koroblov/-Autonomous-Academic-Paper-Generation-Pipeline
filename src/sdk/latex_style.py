import json
from dataclasses import dataclass
from pathlib import Path

from sdk.md_latex import escape_text

_CFG_DEFAULT = Path(__file__).parent.parent.parent / "config" / "setup.json"


@dataclass
class CoverInfo:
    """Metadata fields rendered on the document cover page."""

    subject: str
    authors: str
    date: str
    course: str
    lecturer: str


def load_cover_info(cfg_path: Path = _CFG_DEFAULT) -> CoverInfo:
    """Reads cover page fields from setup.json; subject falls back to paper_generation.subject."""
    with cfg_path.open(encoding="utf-8") as fh:
        cfg = json.load(fh)
    cp = cfg.get("cover_page", {})
    subject_default = cfg.get("paper_generation", {}).get("subject", "")
    return CoverInfo(
        subject=cp.get("subject", subject_default),
        authors=cp.get("authors", ""),
        date=cp.get("date", ""),
        course=cp.get("course", ""),
        lecturer=cp.get("lecturer", ""),
    )


def enhanced_preamble(base: str, info: CoverInfo) -> str:
    """Injects fancyhdr header/footer configuration into base before \\begin{document}."""
    subject_esc = escape_text(info.subject)
    extras = (
        "\\usepackage{fancyhdr}\n"
        "\\setlength{\\headheight}{14pt}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        f"\\fancyhead[C]{{\\small {subject_esc}}}\n"
        "\\fancyfoot[C]{\\thepage}\n"
        "\\renewcommand{\\headrulewidth}{0.4pt}\n"
    )
    return base.replace("\\begin{document}\n", extras + "\\begin{document}\n")


def cover_page_tex(info: CoverInfo) -> str:
    """Returns a LaTeX titlepage block with Subject, Authors, Date, Course, Lecturer."""
    s = escape_text(info.subject)
    a = escape_text(info.authors)
    d = escape_text(info.date)
    c = escape_text(info.course)
    lec = escape_text(info.lecturer)
    lines = [
        "\\begin{titlepage}",
        "\\centering",
        "\\vspace*{3cm}",
        f"{{\\Huge\\bfseries {s}\\par}}",
        "\\vspace{2cm}",
        f"{{\\Large מגיש: {a}\\par}}",
        "\\vspace{1cm}",
        f"{{\\large קורס: {c}\\par}}",
        f"{{\\large מרצה: {lec}\\par}}",
        "\\vfill",
        f"{{\\large {d}\\par}}",
        "\\end{titlepage}",
        "\\newpage",
    ]
    return "\n".join(lines)
