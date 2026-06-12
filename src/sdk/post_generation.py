import logging
from pathlib import Path
from typing import Any, Dict

from sdk.bib_sync import validate_sync, write_bib
from sdk.core import PaperOrchestrator
from sdk.latex_compiler import LatexCompiler
from sdk.tex_sanity import check_tex

logger = logging.getLogger(__name__)


def synchronize_bibliography(md_path: Path, tex_path: Path) -> Dict[str, Any]:
    """
    Builds a RAG-mapped references.bib from the draft, verifies every in-text
    citation resolves to a source (zero broken citations), and runs the
    pre-compilation schema/math sanity check (Gate 4).
    """
    md_text = md_path.read_text(encoding="utf-8")
    bib_path = md_path.parent / "references.bib"
    refs = write_bib(md_text, bib_path)
    sync = validate_sync(md_text, refs)
    sanity = check_tex(tex_path.read_text(encoding="utf-8"), bib_keys={r.key for r in refs})
    if not sync["ok"]:
        logger.warning("Citation synchronization issues: %s", sync)
    if not sanity["ok"]:
        logger.warning("Gate 4 pre-compilation sanity issues: %s", sanity["issues"])
    return {"bib_path": bib_path, "entries": len(refs), "sync": sync, "sanity": sanity}


def verify_length(orchestrator: PaperOrchestrator, tex_path: Path) -> Dict[str, Any]:
    """Compiles the .tex and confirms the TRUE PDF page count against the config target."""
    pg = orchestrator.config.get("paper_generation", {})
    min_pages = pg.get("verify_pages_min", 14)
    max_pages = pg.get("verify_pages_max", 16)
    report = LatexCompiler().verify(tex_path, min_pages, max_pages, out_dir=tex_path.parent / "build")
    logger.info("Page-length confirmation: %s (%s pages).", report["status"], report["page_count"])
    return report
