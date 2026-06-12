import logging
import re
from typing import Dict, List, Optional, Set

from sdk.bib_generator import extract_cite_keys

logger = logging.getLogger(__name__)

_BEGIN_RE = re.compile(r"\\begin\{(\w+\*?)\}")
_END_RE = re.compile(r"\\end\{(\w+\*?)\}")
_COMMENT_RE = re.compile(r"(?<!\\)%.*")


def _strip_comments(tex: str) -> str:
    """Drops LaTeX comments (an unescaped % to end of line) so commented-out
    code is never counted as real structure."""
    return _COMMENT_RE.sub("", tex)


def _math_issues(tex: str) -> List[str]:
    """Flags unbalanced math delimiters: $$ display, $ inline, and \\[ \\] pairs."""
    issues: List[str] = []
    if tex.count("$$") % 2 != 0:
        issues.append("unbalanced $$ display-math delimiters")
    # Remove paired $$ first so a lone $$ does not skew the single-$ count.
    inline_dollars = tex.replace("$$", "").count("$")
    if inline_dollars % 2 != 0:
        issues.append("unbalanced $ inline-math delimiters")
    # \[ \] display math, but not \\[..] which is a line break with spacing.
    if len(re.findall(r"(?<!\\)\\\[", tex)) != len(re.findall(r"(?<!\\)\\\]", tex)):
        issues.append("unbalanced \\[ \\] display-math delimiters")
    return issues


def _structure_issues(tex: str) -> List[str]:
    """Flags unbalanced braces and mismatched \\begin/\\end environments."""
    issues: List[str] = []
    if tex.count("{") != tex.count("}"):
        issues.append("unbalanced { } braces")
    begins = sorted(_BEGIN_RE.findall(tex))
    ends = sorted(_END_RE.findall(tex))
    if begins != ends:
        issues.append(f"mismatched environments: begin={begins} end={ends}")
    return issues


def _citation_issues(tex: str, bib_keys: Set[str]) -> List[str]:
    """Flags \\cite keys that have no matching entry in the bibliography."""
    used = extract_cite_keys(tex)
    unresolved = [k for k in used if k not in bib_keys]
    return [f"unresolved cite keys: {unresolved}"] if unresolved else []


def check_tex(tex: str, bib_keys: Optional[Set[str]] = None) -> Dict[str, object]:
    """
    Pre-compilation schema/math sanity evaluation (Gate 4). Returns a report with
    ok=True only when the .tex has balanced math, balanced braces/environments,
    and (when bib_keys is supplied) no unresolved citation keys. Brace balance is
    a heuristic, but reliably catches the structural breakage that halts LuaLaTeX.
    """
    tex = _strip_comments(tex)
    issues = _math_issues(tex) + _structure_issues(tex)
    if bib_keys is not None:
        issues += _citation_issues(tex, bib_keys)
    report = {"ok": not issues, "issues": issues}
    if issues:
        logger.warning("Pre-compilation sanity FAILED: %s", issues)
    else:
        logger.info("Pre-compilation sanity PASSED (Gate 4).")
    return report
