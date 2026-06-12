import logging
import re
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

from sdk.bib_sync import Reference

logger = logging.getLogger(__name__)

DEFAULT_CORPUS_DIR = Path("data/raw")

_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
# Generic values some PDF producers stamp into the author field; treat as empty.
_PLACEHOLDER_AUTHORS = {"", "user", "unknown", "admin", "owner"}


def _clean(value: str | None) -> str:
    """Collapse whitespace in a metadata string."""
    return re.sub(r"\s+", " ", (value or "").strip())


def _extract(pdf: Path) -> Reference:
    """
    Best-effort bibliographic record for one corpus PDF. Prefers the PDF's
    embedded /Title and /Author metadata, falling back to the first line of
    page-one text for the title and to the filename as a last resort. The year
    is the first 19xx/20xx found on the first page.
    """
    doc = fitz.open(pdf)
    try:
        meta = doc.metadata or {}
        page0 = doc[0].get_text() if doc.page_count else ""
    finally:
        doc.close()

    title = _clean(meta.get("title"))
    if not title:
        lines = [ln.strip() for ln in page0.splitlines() if ln.strip()]
        title = lines[0] if lines else pdf.stem.replace("_", " ")

    author = _clean(meta.get("author"))
    if author.lower() in _PLACEHOLDER_AUTHORS:
        author = ""

    year_match = _YEAR_RE.search(page0)
    year = year_match.group(0) if year_match else "n.d."

    return Reference(
        number=0,
        key=pdf.stem,
        author=author or "Unknown",
        title=title,
        year=year,
        filename=pdf.name,
        page="1",
        raw=title,
    )


def corpus_references(raw_dir: str | Path = DEFAULT_CORPUS_DIR) -> List[Reference]:
    """One Reference per PDF in the corpus directory (sorted by filename), so a
    bibliography can always be grounded in the real source documents even when
    the draft itself never listed them."""
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        logger.warning("Corpus directory %s not found; no fallback references available.", raw_dir)
        return []
    return [_extract(p) for p in sorted(raw_dir.glob("*.pdf"))]
