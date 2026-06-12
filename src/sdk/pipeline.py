import logging
import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from sdk.core import PaperOrchestrator
from sdk.hil_gate import HumanInLoopGate
from sdk.ingest import CorpusIngestor
from sdk.latex_converter import LatexConverter
from sdk.latex_style import load_cover_info
from sdk.post_generation import synchronize_bibliography
from sdk.post_generation import verify_length as verify_page_length
from tools.rag_core import RAGCore

logger = logging.getLogger(__name__)

TRANSIENT_MARKERS = ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "overloaded")
GEN_MAX_RETRIES = 5
GEN_RETRY_DELAY = 30.0
GEN_BACKOFF_FACTOR = 2.0
GEN_MAX_DELAY = 300.0

# Server-advised retry hints, e.g. "Retry-After: 41", "retry_delay { seconds: 41 }",
# or litellm's "'retryDelay': '41s'". The first numeric group is the delay in seconds.
_RETRY_AFTER_PATTERNS = (
    re.compile(r"retry-after['\"]?\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)", re.IGNORECASE),
    re.compile(
        r"retry[_-]?delay['\"]?\s*[:={(]+\s*(?:seconds['\"]?\s*[:=]\s*)?['\"]?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    ),
)


def _parse_retry_after(err_str: str) -> Optional[float]:
    """Extracts a server-advised retry delay (seconds) from an API error, if present."""
    for pattern in _RETRY_AFTER_PATTERNS:
        match = pattern.search(err_str)
        if match:
            return min(float(match.group(1)), GEN_MAX_DELAY)
    return None


def _retry_delay(attempt: int, err_str: str, base: float) -> float:
    """Honors a server Retry-After hint, else exponential backoff capped at GEN_MAX_DELAY."""
    advised = _parse_retry_after(err_str)
    if advised is not None:
        return advised
    return min(base * (GEN_BACKOFF_FACTOR**attempt), GEN_MAX_DELAY)


def _run_with_retry(
    orchestrator: PaperOrchestrator,
    retries: int = GEN_MAX_RETRIES,
    delay: float = GEN_RETRY_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    """Runs the crew, retrying transient Gemini 503/429 spikes with exponential
    backoff (or a server-advised Retry-After delay when the API supplies one)."""
    for attempt in range(retries):
        try:
            return orchestrator.run()
        except Exception as e:
            err_str = str(e)
            transient = any(marker in err_str for marker in TRANSIENT_MARKERS)
            if transient and attempt < retries - 1:
                wait = _retry_delay(attempt, err_str, delay)
                logger.warning(f"Transient API error; retrying in {wait}s (attempt {attempt + 1}/{retries}).")
                sleep(wait)
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
    verify_length: bool = False,
) -> Dict[str, Any]:
    """
    Full end-to-end flow: ensure corpus -> generate draft via the CrewAI crew ->
    enforce the hard Human-in-the-Loop Positive AI Economy gate. When
    verify_length is set, the .tex is compiled to PDF and its true page count is
    confirmed against the target. Returns a dict with the crew result, output
    path, the HIL approval record, and (optionally) the length report.
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
    LatexConverter().convert_file(md_path, tex_path, cover=load_cover_info())
    logger.info(f"Compile-ready LaTeX written to {tex_path}")

    bibliography = synchronize_bibliography(md_path, tex_path)

    gate = gate or HumanInLoopGate(auto_approve=auto_approve_hil)
    approval = gate.request_approval(tex_path)

    outcome: Dict[str, Any] = {
        "result": result,
        "output_path": md_path,
        "tex_path": tex_path,
        "approval": approval,
        "bibliography": bibliography,
    }
    if verify_length:
        outcome["length_report"] = verify_page_length(orchestrator, tex_path)
    return outcome
