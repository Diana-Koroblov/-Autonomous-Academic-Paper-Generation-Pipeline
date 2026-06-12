import logging
import re
from pathlib import Path
from typing import List, Optional

from sdk.bib_sync import REFERENCES_HEADINGS, in_text_numbers
from sdk.latex_style import CoverInfo, cover_page_tex, enhanced_preamble
from sdk.md_latex import MAX_CITE, POSTAMBLE, PREAMBLE, figure_block, inline, md_table, placeholder_box, title_block

logger = logging.getLogger(__name__)


class LatexConverter:
    """
    Transforms the raw academic Markdown draft into a complete, compilable
    LuaLaTeX document: emits a BiDi preamble, maps Markdown headings/lists/tables
    /bold to LaTeX, renders `$$...$$` as display math, turns `[TOC]` into a real
    table of contents, and replaces missing-asset placeholders ([IMAGE], [DATA
    GRAPH], [TIKZ DIAGRAM]) with framed boxes so the document lays out and the
    true page count can be measured.
    """

    def __init__(self) -> None:
        self._list_mode: Optional[str] = None
        self._in_refs: bool = False
        # >0 while inside a raw LaTeX environment the draft emitted itself
        # (e.g. \begin{figure}/\begin{tikzpicture}/\begin{table}); such lines are
        # passed through verbatim instead of being escaped into visible source.
        self._latex_depth: int = 0
        # Shallowest Markdown heading level in the draft, so headings map onto
        # section/subsection/subsubsection regardless of whether the writer used
        # '#' or '##' as its top level.
        self._min_depth: int = 1

    def _open_list(self, out: List[str], mode: str) -> None:
        if self._list_mode != mode:
            self._close_list(out)
            out.append(f"\\begin{{{mode}}}")
            self._list_mode = mode

    def _close_list(self, out: List[str]) -> None:
        if self._list_mode:
            out.append(f"\\end{{{self._list_mode}}}")
            self._list_mode = None

    def _emit_block(self, s: str, out: List[str]) -> bool:
        """Handles a single non-table, non-blank line. Returns True if consumed."""
        if s in ("***", "---", "___"):
            self._close_list(out)
            return True
        if s == "[TOC]":
            self._close_list(out)
            out.append("\\tableofcontents\n\\newpage")
            return True
        if s == "[DRAKE EQUATION]":
            self._close_list(out)
            return True
        math = re.fullmatch(r"\$\$(.+)\$\$", s)
        if math:
            self._close_list(out)
            out.append("\\[" + math.group(1).strip() + "\\]")
            return True
        asset_m = re.match(r"\[(IMAGE|DATA GRAPH|TIKZ DIAGRAM)\s+(\S+)\s*[-—–]+\s*(.+)\]", s)
        if asset_m or re.match(r"\[(IMAGE|DATA GRAPH|TIKZ DIAGRAM)\b[^\]]*\]", s):
            self._close_list(out)
            block = figure_block(asset_m.group(2), asset_m.group(3).strip()) if asset_m \
                else placeholder_box(s.strip("[]"))
            out.append(block)
            return True
        if re.match(r"\[TABLE\b[^\]]*\]", s):  # caption marker; the tabular follows
            self._close_list(out)
            return True
        return self._emit_heading_or_list(s, out)

    @staticmethod
    def _heading_depths(lines: List[str]) -> List[int]:
        return [len(m.group(1)) for line in lines if (m := re.match(r"(#{1,6})\s+\S", line.strip()))]

    def _emit_heading_or_list(self, s: str, out: List[str]) -> bool:
        head = re.match(r"(#{1,6})\s+(.*)", s)
        if head:
            self._close_list(out)
            level = min(max(len(head.group(1)) - self._min_depth, 0), 2)
            cmd = ("section", "subsection", "subsubsection")[level]
            out.append("\\" + cmd + "{" + inline(head.group(2)) + "}")
            return True
        bullet = re.match(r"\*\s+(.+)", s)
        if bullet:
            self._open_list(out, "itemize")
            out.append("\\item " + inline(bullet.group(1)))
            return True
        numbered = re.match(r"(\d+)\.\s+(.+)", s)
        if numbered:
            self._open_list(out, "enumerate")
            out.append("\\item " + inline(numbered.group(2)))
            return True
        return False

    def _is_references_heading(self, stripped: str) -> bool:
        head = re.match(r"(?:#{1,3}\s+|\\(?:chapter|section)\{)(.*?)(?:\}|$)", stripped)
        return bool(head and any(h in head.group(1) for h in REFERENCES_HEADINGS))

    def convert(self, raw: str, cover: Optional[CoverInfo] = None) -> str:
        """Returns a complete, compilable .tex string built from the raw draft."""
        preamble = enhanced_preamble(PREAMBLE, cover) if cover else PREAMBLE
        out: List[str] = [preamble]
        if cover:
            out.append(cover_page_tex(cover))
        # Seed \nocite in citation order so biblatex (sorting=none) numbers the
        # bibliography to match the writer's existing [1], [2], ... markers.
        nums = sorted(in_text_numbers(raw))[:MAX_CITE]
        if nums:
            out.append("\\nocite{" + ",".join(f"ref{n}" for n in nums) + "}")
        lines = raw.splitlines()
        depths = self._heading_depths(lines)
        self._min_depth = min(depths) if depths else 1
        self._list_mode = None
        self._in_refs = False
        self._latex_depth = 0
        table_buf: List[str] = []
        title_done = False
        for line in lines:
            stripped = line.strip()
            if self._in_refs:  # entries are captured in references.bib; skip the raw list
                continue
            if stripped.startswith("```"):  # drop Markdown code-fence markers
                continue
            if stripped.startswith("%"):  # drop standalone LaTeX comments (e.g. the model's example preamble)
                continue
            # Catch \chapter{רשימת מקורות} (and similar) BEFORE the verbatim
            # passthrough, so a LaTeX-style references heading is properly
            # intercepted and does not end up printed as raw body text.
            if self._latex_depth == 0 and self._is_references_heading(stripped):
                if table_buf:
                    self._close_list(out)
                    out.append(md_table(table_buf))
                    table_buf = []
                self._close_list(out)
                out.append("\\printbibliography[title={רשימת מקורות}]")
                self._in_refs = True
                continue
            # Pass raw LaTeX through verbatim. The writer may emit whole
            # environments itself; escaping them would print the source.
            if self._latex_depth > 0 or stripped.startswith("\\"):
                if table_buf:
                    self._close_list(out)
                    out.append(md_table(table_buf))
                    table_buf = []
                self._close_list(out)
                out.append(line)
                self._latex_depth = max(
                    0, self._latex_depth + stripped.count("\\begin{") - stripped.count("\\end{")
                )
                continue
            if stripped.startswith("|"):
                table_buf.append(line)
                continue
            if table_buf:
                self._close_list(out)
                out.append(md_table(table_buf))
                table_buf = []
            if not stripped:
                self._close_list(out)
                out.append("")
                continue
            if self._is_references_heading(stripped):
                self._close_list(out)
                out.append("\\printbibliography[title={רשימת מקורות}]")
                self._in_refs = True
                continue
            if not title_done:
                title_done = True
                if stripped.startswith("**") and stripped.endswith("**"):
                    out.append(title_block(stripped))
                    continue
                htitle = re.match(r"#{1,6}\s+(.*)", stripped)
                if htitle:  # a leading heading stands in as the document title
                    out.append(title_block("**" + htitle.group(1).strip() + "**"))
                    continue
            if not self._emit_block(stripped, out):
                self._close_list(out)
                out.append(inline(line))
        if table_buf:
            out.append(md_table(table_buf))
        self._close_list(out)
        # If the draft never included a reference list, still print the
        # bibliography so the (corpus-grounded) citations have a target section.
        if not self._in_refs:
            out.append("\\newpage")
            out.append("\\printbibliography[title={רשימת מקורות}]")
        out.append(POSTAMBLE)
        return "\n".join(out) + "\n"

    def convert_file(self, src: str | Path, dst: str | Path, cover: Optional[CoverInfo] = None) -> Path:
        """Converts a raw draft file and writes the compilable .tex to dst."""
        raw = Path(src).read_text(encoding="utf-8")
        tex = self.convert(raw, cover=cover)
        dst_path = Path(dst)
        dst_path.write_text(tex, encoding="utf-8")
        logger.info("Wrote compilable LaTeX to %s (%d lines).", dst_path, tex.count("\n"))
        return dst_path
