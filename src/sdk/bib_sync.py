import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

# Headings (Hebrew/English) that mark the start of the draft's reference list.
REFERENCES_HEADINGS = ("רשימת מקורות", "ביבליוגרפיה", "References", "Bibliography")

_HEADING_RE = re.compile(r"#{1,3}\s+(.*)")
_ENTRY_RE = re.compile(r"^\[(\d+)\]\s*(.*)$")
_SOURCE_RE = re.compile(r"([A-Za-z0-9_\-]+\.pdf)\s*#?\s*page\s*=?\s*(\d+)", re.IGNORECASE)
_YEAR_RE = re.compile(r"\((\d{4})\)")
_TITLE_RE = re.compile(r"\*([^*]+)\*")
_INTEXT_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


@dataclass
class Reference:
    """A single bibliography entry tied back to its RAG source PDF + page."""

    number: int
    key: str
    author: str
    title: str
    year: str
    filename: str
    page: str
    raw: str


def _references_start(lines: List[str]) -> int | None:
    """Index of the first reference-entry line (just after the references heading)."""
    for idx, line in enumerate(lines):
        heading = _HEADING_RE.match(line.strip())
        if heading and any(h in heading.group(1) for h in REFERENCES_HEADINGS):
            return idx + 1
    return None


def parse_references(md_text: str) -> List[Reference]:
    """Extracts RAG-backed Reference records from the draft's reference list."""
    lines = md_text.splitlines()
    start = _references_start(lines)
    refs: List[Reference] = []
    if start is None:
        return refs
    for line in lines[start:]:
        entry = _ENTRY_RE.match(line.strip())
        if not entry:
            continue
        number, body = int(entry.group(1)), entry.group(2)
        source = _SOURCE_RE.search(body)
        filename = source.group(1) if source else ""
        page = source.group(2) if source else ""
        year = _YEAR_RE.search(body)
        title = _TITLE_RE.search(body)
        author = body.split("(")[0].strip().rstrip(".") or "Unknown"
        refs.append(
            Reference(
                number=number,
                key=f"ref{number}",
                author=author,
                title=title.group(1).strip() if title else (body[:60].strip() or f"Reference {number}"),
                year=year.group(1) if year else "n.d.",
                filename=filename,
                page=page,
                raw=body.strip(),
            )
        )
    return refs


def _clean(text: str) -> str:
    """Strips characters that would break a BibTeX field value (& -> 'and')."""
    return re.sub(r"[{}\\*]", "", text).replace("&", "and").strip()


def _bib_entry(r: Reference) -> str:
    """One @misc entry. Author is double-braced as a literal name so its commas
    and initials are not parsed as BibTeX name separators (biber rejects names
    with too many commas). Year is emitted only when it is a real 4-digit year."""
    note = f"RAG source: {r.filename}, page {r.page}" if r.filename else "RAG source: unmapped"
    literal_author = "{" + _clean(r.author) + "}"
    lines = [
        "@misc{" + r.key + ",",
        "  author = {" + literal_author + "},",
        "  title  = {" + _clean(r.title) + "},",
    ]
    if re.fullmatch(r"\d{4}", r.year):
        lines.append("  year   = {" + r.year + "},")
    lines.append("  note   = {" + note + "}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_bib(refs: List[Reference]) -> str:
    """Renders RAG-backed Reference records as a real BibTeX @misc bibliography."""
    if not refs:
        return ""
    header = "% Auto-generated from the draft's reference list, mapped to RAG source metadata.\n\n"
    return header + "\n".join(_bib_entry(r) for r in refs)


def in_text_numbers(md_text: str) -> Set[int]:
    """Citation numbers used in the body (everything before the references list)."""
    lines = md_text.splitlines()
    start = _references_start(lines)
    body = "\n".join(lines[: start - 1] if start is not None else lines)
    numbers: Set[int] = set()
    for group in _INTEXT_RE.findall(body):
        for n in group.split(","):
            numbers.add(int(n.strip()))
    return numbers


def validate_sync(md_text: str, refs: List[Reference]) -> Dict[str, object]:
    """
    Confirms every in-text [N] resolves to a RAG-mapped reference. ok is True only
    when there are zero broken citations and every cited entry carries source
    metadata (filename + page).
    """
    by_number = {r.number: r for r in refs}
    cited = in_text_numbers(md_text)
    broken = sorted(n for n in cited if n not in by_number)
    missing_metadata = sorted(r.number for r in refs if r.number in cited and not (r.filename and r.page))
    unused = sorted(r.number for r in refs if r.number not in cited)
    return {
        "ok": not broken and not missing_metadata,
        "cited": sorted(cited),
        "total_refs": len(refs),
        "broken_citations": broken,
        "missing_metadata": missing_metadata,
        "unused_refs": unused,
    }


def write_bib(md_text: str, bib_path: str | Path) -> List[Reference]:
    """Parses references from the draft and writes references.bib. Returns the records."""
    refs = parse_references(md_text)
    Path(bib_path).write_text(build_bib(refs), encoding="utf-8")
    logger.info("Wrote %d RAG-mapped bibliography entries to %s.", len(refs), bib_path)
    return refs
