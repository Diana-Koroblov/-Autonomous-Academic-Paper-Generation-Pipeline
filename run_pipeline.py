import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sdk.pipeline import run_pipeline  # noqa: E402


def _force_utf8_io() -> None:
    """Reconfigure console streams to UTF-8 so Hebrew/ligature output cannot crash on Windows cp1252."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def main() -> dict:
    """Entry point: load credentials and execute the full generation pipeline."""
    _force_utf8_io()
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    auto_approve = "--auto-approve-hil" in sys.argv
    skip_ingestion = "--skip-ingestion" in sys.argv
    outcome = run_pipeline(auto_approve_hil=auto_approve, skip_ingestion=skip_ingestion)
    log = logging.getLogger(__name__)
    log.info(f"Pipeline finished. Raw draft: {outcome['output_path']}")
    log.info(f"Compile-ready LaTeX (compile this): {outcome['tex_path']}")
    return outcome


if __name__ == "__main__":
    main()
