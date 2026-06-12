import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# LuaLaTeX/pdfTeX emit this line on a successful run, e.g.
# "Output written on output.pdf (15 pages, 123456 bytes)."
_PAGE_RE = re.compile(r"Output written on .*?\((\d+)\s+pages?", re.IGNORECASE)

DEFAULT_ENGINE = "lualatex"
# Generous: a biblatex+biber BiDi build runs several passes, and a first run may
# fetch missing MiKTeX packages on demand before any pass completes.
DEFAULT_TIMEOUT = 1200


class LatexCompiler:
    """
    Compiles a `.tex` document to PDF via latexmk + LuaLaTeX (which handles the
    multi-pass reruns needed to populate the table of contents) and reports the
    TRUE page count parsed from the compiler log. Page count is a compile-time
    fact, so this is the only authoritative confirmation of document length.
    """

    def __init__(
        self,
        engine: str = DEFAULT_ENGINE,
        timeout: int = DEFAULT_TIMEOUT,
        runner: Callable[..., Any] = subprocess.run,
    ) -> None:
        self.engine = engine
        self.timeout = timeout
        self._runner = runner

    def _build_cmd(self, tex_path: Path, out_dir: Path) -> list[str]:
        """latexmk invocation: nonstopmode so a stray error never blocks the PDF."""
        return [
            "latexmk",
            f"-{self.engine}",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-cd",  # change to source dir so relative paths (assets/, .bib) resolve
            f"-outdir={out_dir.resolve()}",
            str(tex_path),
        ]

    def _page_count_from_log(self, log_path: Path) -> Optional[int]:
        """Parses the 'Output written on ... (N pages' line from the engine log."""
        if not log_path.exists():
            return None
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        matches = _PAGE_RE.findall(log_text)
        return int(matches[-1]) if matches else None

    def compile(self, tex_path: str | Path, out_dir: str | Path | None = None) -> Dict[str, Any]:
        """
        Runs the compile and returns a result dict: pdf_path (if produced),
        page_count (int or None), ok (bool), and the raw stdout for diagnostics.
        """
        tex_path = Path(tex_path)
        out_dir = Path(out_dir) if out_dir else tex_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # Copy sibling .bib files into the out dir so biber (auto-run by latexmk
        # for biblatex documents) can resolve \addbibresource.
        if out_dir.resolve() != tex_path.parent.resolve():
            for bib in tex_path.parent.glob("*.bib"):
                shutil.copy(bib, out_dir / bib.name)

        proc = self._runner(
            self._build_cmd(tex_path, out_dir),
            capture_output=True,
            text=True,
            timeout=self.timeout,
            encoding="utf-8",
            errors="replace",
        )
        pdf_path = out_dir / f"{tex_path.stem}.pdf"
        log_path = out_dir / f"{tex_path.stem}.log"
        page_count = self._page_count_from_log(log_path)
        ok = pdf_path.exists() and page_count is not None
        if not ok:
            logger.error("LaTeX compile did not yield a PDF. Exit=%s", getattr(proc, "returncode", "?"))
        return {
            "ok": ok,
            "pdf_path": pdf_path if pdf_path.exists() else None,
            "page_count": page_count,
            "returncode": getattr(proc, "returncode", None),
            "stdout": getattr(proc, "stdout", ""),
        }

    def verify(
        self,
        tex_path: str | Path,
        min_pages: int,
        max_pages: int,
        out_dir: str | Path | None = None,
    ) -> Dict[str, Any]:
        """Compiles, then reports whether the true page count is within [min, max]."""
        result = self.compile(tex_path, out_dir)
        pages = result["page_count"]
        if pages is None:
            result["status"] = "COMPILE_FAILED"
            result["within_target"] = False
        elif pages < min_pages:
            result["status"] = "SHORT"
            result["within_target"] = False
        elif pages > max_pages:
            result["status"] = "OVER"
            result["within_target"] = False
        else:
            result["status"] = "PASS"
            result["within_target"] = True
        result["target"] = (min_pages, max_pages)
        logger.info(
            "Length verification: %s (%s pages, target %d-%d).",
            result["status"],
            pages,
            min_pages,
            max_pages,
        )
        return result
