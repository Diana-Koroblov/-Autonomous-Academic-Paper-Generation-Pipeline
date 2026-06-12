import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
_AUTHOR_RE = re.compile(r"^([A-Z][a-z]+(,?\s+[A-Z][a-z]*\.?)+(?:\s+(?:and|&)\s+[A-Z][a-z]+)?)")


def _extract_year(text: str) -> str:
    m = _YEAR_RE.search(text)
    return m.group(0) if m else "n.d."


def _extract_author(text: str) -> str:
    m = _AUTHOR_RE.match(text.strip())
    return m.group(0).strip() if m else ""


def web_search(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Searches the web via DuckDuckGo and returns structured article metadata.
    Each result has: title, url, snippet, author (best-effort), year (best-effort).
    Focuses on academic/news sources relevant to the query.
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        logger.error("duckduckgo-search is not installed. Run: uv add duckduckgo-search")
        return []

    academic_query = f"{query} site:arxiv.org OR site:researchgate.net OR site:scholar.google.com OR site:pubmed.ncbi.nlm.nih.gov OR site:semanticscholar.org"
    results: List[Dict[str, Any]] = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(academic_query, max_results=max_results):
                snippet = r.get("body", "")
                results.append({
                    "title": r.get("title", "Untitled"),
                    "url": r.get("href", ""),
                    "snippet": snippet,
                    "author": _extract_author(snippet),
                    "year": _extract_year(snippet),
                })
    except Exception as e:
        logger.warning("Academic DuckDuckGo search failed (%s); falling back to open query.", e)

    # Fallback: open query if academic-filtered search returned nothing
    if not results:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    snippet = r.get("body", "")
                    results.append({
                        "title": r.get("title", "Untitled"),
                        "url": r.get("href", ""),
                        "snippet": snippet,
                        "author": _extract_author(snippet),
                        "year": _extract_year(snippet),
                    })
        except Exception as e:
            logger.error("DuckDuckGo search error: %s", e)

    logger.info("web_search(%r) → %d results", query, len(results))
    return results


def format_web_results(results: List[Dict[str, Any]]) -> str:
    """Formats search results as structured text for the researcher agent."""
    if not results:
        return "No web results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[Result {i}]")
        lines.append(f"  Title:   {r['title']}")
        lines.append(f"  URL:     {r['url']}")
        lines.append(f"  Author:  {r['author'] or '(unknown)'}")
        lines.append(f"  Year:    {r['year']}")
        lines.append(f"  Snippet: {r['snippet'][:300]}")
        lines.append("")
    return "\n".join(lines)
