import logging
import re
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# Robust Hebrew BiDi preamble for LuaLaTeX. babel's bidi=basic reliably renders
# embedded English (Latin) runs left-to-right inside the right-to-left Hebrew flow,
# which polyglossia does not do dependably on LuaLaTeX.
BIDI_PREAMBLE = (
    "% --- BiDi Setup (LuaLaTeX + babel) ---\n"
    "\\usepackage{fontspec}\n"
    "\\usepackage[bidi=basic]{babel}\n"
    "\\babelprovide[main, import]{hebrew}\n"
    "\\babelprovide[import]{english}\n"
    "\\babelfont{rm}{Arial}\n"
)

# Preamble lines that must be removed (polyglossia/manual font setup is replaced
# by BIDI_PREAMBLE) or that are invalid/hallucinated commands.
_DROP_PREFIXES = (
    "\\usepackage{polyglossia}",
    "\\usepackage{fontspec}",
    "\\setmainlanguage",
    "\\setotherlanguage",
    "\\setcode",
    "\\setmainfont",
    "\\setsansfont",
    "\\newfontfamily",
)


class LatexConverter:
    """
    Transforms raw AI Markdown/LaTeX output into a compilable LuaLaTeX document:
    strips Markdown code fences, removes invalid commands, converts leaked
    Markdown bold, drops the polyglossia language environment, and injects a
    babel BiDi preamble so Hebrew is RTL and embedded English is LTR.
    """

    def _sanitize_line(self, line: str) -> str:
        line = line.replace("\\tableofcontents*", "\\tableofcontents")
        # Paired Markdown bold -> LaTeX bold.
        line = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", line)
        # A stray, unpaired '**' is the model closing an opened \textbf{ with
        # Markdown syntax; map it back to the missing closing brace.
        if "**" in line:
            logger.warning("Converting stray Markdown '**' to closing brace in: %s", line.strip()[:60])
            line = line.replace("**", "}")
        return line

    def convert(self, raw: str) -> str:
        """Returns a compilable .tex string built from the raw agent output."""
        out: List[str] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped in ("```latex", "```"):  # drop Markdown code fences
                continue
            if stripped in ("\\begin{hebrew}", "\\end{hebrew}"):  # polyglossia env
                continue
            if any(stripped.startswith(prefix) for prefix in _DROP_PREFIXES):
                continue
            if stripped == "\\begin{document}":
                out.append(BIDI_PREAMBLE)
            out.append(self._sanitize_line(line))
        return "\n".join(out) + "\n"

    def convert_file(self, src: str | Path, dst: str | Path) -> Path:
        """Converts a raw output file and writes the compilable .tex to dst."""
        raw = Path(src).read_text(encoding="utf-8")
        tex = self.convert(raw)
        dst_path = Path(dst)
        dst_path.write_text(tex, encoding="utf-8")
        logger.info("Wrote compilable LaTeX to %s (%d lines).", dst_path, tex.count("\n"))
        return dst_path
