import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from sdk.bib_sync import Reference

logger = logging.getLogger(__name__)

# Per-run sink for sources the researcher actually pulled off the web. The web
# tool only returns its hits into the agent's context, so without this they are
# lost before the bibliography is built. Capturing them here lets the .bib step
# ground real \cite keys in genuine online sources (with URLs).
WEB_SOURCES_PATH = Path("data/processed/web_sources.json")


def clear_web_sources(path: Path = WEB_SOURCES_PATH) -> None:
    """Deletes any web sources left over from a previous run so each run is fresh."""
    try:
        Path(path).unlink()
    except FileNotFoundError:
        pass


def record_web_sources(results: List[Dict[str, Any]], path: Path = WEB_SOURCES_PATH) -> int:
    """
    Appends web-search hits to the run's sink, de-duplicated by URL. Each result
    is the dict shape produced by tools.web_search.web_search (title/url/author/
    year/snippet). Returns the total number of stored sources.
    """
    path = Path(path)
    existing: List[Dict[str, Any]] = []
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = []

    by_url: Dict[str, Dict[str, Any]] = {r["url"]: r for r in existing if r.get("url")}
    for r in results:
        url = (r.get("url") or "").strip()
        if url and url not in by_url:
            by_url[url] = r

    merged = list(by_url.values())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Recorded %d web source(s) → %s", len(merged), path)
    return len(merged)


def load_web_references(path: Path = WEB_SOURCES_PATH) -> List[Reference]:
    """
    Loads captured web sources as Reference records carrying a url (and no corpus
    filename/page), ready to ground \\cite keys that the draft never mapped.
    """
    path = Path(path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("Could not parse web sources at %s; ignoring.", path)
        return []

    refs: List[Reference] = []
    for r in data:
        url = (r.get("url") or "").strip()
        if not url:
            continue
        refs.append(
            Reference(
                number=0,
                key="web",
                author=r.get("author") or "Unknown",
                title=r.get("title") or url,
                year=r.get("year") or "n.d.",
                filename="",
                page="",
                raw=r.get("snippet", ""),
                url=url,
            )
        )
    return refs
