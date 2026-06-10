import logging
import re
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

_CITE_RE = re.compile(r"\\(?:cite|parencite|textcite|footcite)\{([^}]*)\}")


def extract_cite_keys(tex: str) -> List[str]:
    """Returns the sorted, de-duplicated set of citation keys used in a .tex string."""
    keys = set()
    for match in _CITE_RE.findall(tex):
        for raw in match.split(","):
            key = raw.strip()
            if key:
                keys.add(key)
    return sorted(keys)


def key_to_entry(key: str) -> str:
    """
    Builds a best-effort BibTeX @book entry from an `author_titleword_year` key.
    The trailing numeric segment becomes the year; the first segment is treated
    as the author surname and the remainder as the title.
    """
    parts = [p for p in key.split("_") if p]
    year = "n.d."
    if parts and parts[-1].isdigit():
        year = parts[-1]
        parts = parts[:-1]
    author = parts[0].capitalize() if parts else key
    title_words = parts[1:] if len(parts) > 1 else parts
    title = " ".join(word.capitalize() for word in title_words) or key
    return f"@book{{{key},\n  author = {{{author}}},\n  title  = {{{title}}},\n  year   = {{{year}}}\n}}\n"


def generate_bib(tex_path: str | Path, bib_path: str | Path) -> int:
    """
    Scans a .tex file for citation keys and writes a `references.bib` with a
    matching entry per key, so biblatex/biber can resolve every \\cite.
    Returns the number of entries written.
    """
    tex = Path(tex_path).read_text(encoding="utf-8")
    keys = extract_cite_keys(tex)
    if not keys:
        logger.warning("No citation keys found in %s; no .bib written.", tex_path)
        return 0

    header = "% Auto-generated from \\cite keys. Stub entries — not RAG-verified.\n\n"
    body = "\n".join(key_to_entry(key) for key in keys)
    Path(bib_path).write_text(header + body, encoding="utf-8")
    logger.info("Wrote %d bibliography entries to %s.", len(keys), bib_path)
    return len(keys)
