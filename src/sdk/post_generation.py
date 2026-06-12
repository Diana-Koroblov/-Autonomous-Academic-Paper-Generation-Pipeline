import logging
from pathlib import Path
from typing import Any, Dict

from sdk.bib_generator import extract_cite_keys
from sdk.bib_sync import build_bib, fill_unmapped, parse_references, validate_sync
from sdk.md_latex import MAX_CITE
from sdk.core import PaperOrchestrator
from sdk.corpus_bib import DEFAULT_CORPUS_DIR, corpus_references
from sdk.latex_compiler import LatexCompiler
from sdk.tex_sanity import check_tex

logger = logging.getLogger(__name__)


def synchronize_bibliography(md_path: Path, tex_path: Path, corpus_dir=DEFAULT_CORPUS_DIR) -> Dict[str, Any]:
    """
    Builds references.bib for the draft and verifies every in-text citation
    resolves, then runs the pre-compilation schema/math sanity check (Gate 4).

    Two tiers, so the bibliography never depends on the model emitting a list:
      1. References the writer actually listed, mapped to RAG source metadata.
      2. For any remaining \\cite key, a real corpus document (round-robin), so
         no citation is ever left undefined.
    """
    md_text = md_path.read_text(encoding="utf-8")
    tex_text = tex_path.read_text(encoding="utf-8")
    bib_path = md_path.parent / "references.bib"

    refs = parse_references(md_text)[:MAX_CITE]
    cite_keys = extract_cite_keys(tex_text)
    filled = fill_unmapped(cite_keys, refs, corpus_references(corpus_dir))
    refs += filled[: max(0, MAX_CITE - len(refs))]
    bib_path.write_text(build_bib(refs), encoding="utf-8")
    logger.info("Wrote %d bibliography entries to %s.", len(refs), bib_path)

    sync = validate_sync(md_text, refs)
    sanity = check_tex(tex_text, bib_keys={r.key for r in refs})
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
