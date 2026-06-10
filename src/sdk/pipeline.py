import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from sdk.core import PaperOrchestrator
from sdk.hil_gate import HumanInLoopGate
from sdk.ingest import CorpusIngestor
from sdk.latex_converter import LatexConverter
from tools.rag_core import RAGCore

logger = logging.getLogger(__name__)

TRANSIENT_MARKERS = ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "overloaded")
GEN_MAX_RETRIES = 5
GEN_RETRY_DELAY = 30.0


def _run_with_retry(
    orchestrator: PaperOrchestrator,
    retries: int = GEN_MAX_RETRIES,
    delay: float = GEN_RETRY_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    """Runs the crew, retrying on transient Gemini 503/429 spikes with backoff."""
    for attempt in range(retries):
        try:
            return orchestrator.run()
        except Exception as e:
            transient = any(marker in str(e) for marker in TRANSIENT_MARKERS)
            if transient and attempt < retries - 1:
                logger.warning(f"Transient API error; retrying in {delay}s (attempt {attempt + 1}/{retries}).")
                sleep(delay)
                continue
            raise


def ensure_corpus(core: Optional[RAGCore] = None) -> int:
    """
    Guarantees the vector DB is populated before generation. If the collection
    is empty, the corpus is ingested on demand. Returns the vector count.
    """
    core = core or RAGCore()
    count = core.get_collection().count()
    if count > 0:
        logger.info(f"Vector DB already populated with {count} vectors; skipping ingestion.")
        return count
    logger.info("Vector DB empty; triggering on-demand corpus ingestion.")
    return CorpusIngestor(core=core).ingest()


def run_pipeline(
    orchestrator: Optional[PaperOrchestrator] = None,
    gate: Optional[HumanInLoopGate] = None,
    auto_approve_hil: bool = False,
    skip_ingestion: bool = False,
) -> Dict[str, Any]:
    """
    Full end-to-end flow: ensure corpus -> generate draft via the CrewAI crew ->
    enforce the hard Human-in-the-Loop Positive AI Economy gate. Returns a dict
    with the crew result, output path, and the HIL approval record.
    """
    if not skip_ingestion:
        ensure_corpus()

    orchestrator = orchestrator or PaperOrchestrator()
    logger.info("Launching CrewAI generation flow.")
    result = _run_with_retry(orchestrator)

    # Convert the raw draft into a compile-ready .tex so the reviewer can
    # compile and inspect it during the HIL pause below.
    md_path = Path(orchestrator.output_path)
    tex_path = md_path.with_suffix(".tex")
    LatexConverter().convert_file(md_path, tex_path)
    logger.info(f"Compile-ready LaTeX written to {tex_path}")

    gate = gate or HumanInLoopGate(auto_approve=auto_approve_hil)
    approval = gate.request_approval(tex_path)

    return {
        "result": result,
        "output_path": md_path,
        "tex_path": tex_path,
        "approval": approval,
    }
