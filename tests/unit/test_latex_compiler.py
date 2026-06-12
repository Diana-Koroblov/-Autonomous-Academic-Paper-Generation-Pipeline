import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.latex_compiler import LatexCompiler


class _FakeProc:
    def __init__(self, returncode=0, stdout=""):
        self.returncode = returncode
        self.stdout = stdout


def _make_runner(out_dir: Path, stem: str, pages, make_pdf=True):
    """Returns a fake subprocess.run that drops a synthetic log/pdf like LuaLaTeX."""

    def runner(cmd, **kwargs):
        if pages is not None:
            (out_dir / f"{stem}.log").write_text(
                f"This is LuaTeX...\nOutput written on {stem}.pdf ({pages} pages, 100 bytes).\n",
                encoding="utf-8",
            )
        if make_pdf:
            (out_dir / f"{stem}.pdf").write_bytes(b"%PDF-1.5")
        return _FakeProc()

    return runner


def _tex(tmp_path: Path) -> Path:
    p = tmp_path / "paper.tex"
    p.write_text("\\documentclass{article}\\begin{document}x\\end{document}", encoding="utf-8")
    return p


def test_build_cmd_uses_latexmk_and_engine(tmp_path):
    comp = LatexCompiler(engine="lualatex")
    cmd = comp._build_cmd(_tex(tmp_path), tmp_path)
    assert cmd[0] == "latexmk"
    assert "-lualatex" in cmd
    assert any(c.startswith("-outdir=") for c in cmd)


def test_compile_ok_parses_pages(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=15))
    result = comp.compile(tex, out_dir=tmp_path)
    assert result["ok"] is True
    assert result["page_count"] == 15
    assert result["pdf_path"] is not None


def test_compile_no_pdf_is_not_ok(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=15, make_pdf=False))
    result = comp.compile(tex, out_dir=tmp_path)
    assert result["ok"] is False
    assert result["pdf_path"] is None


def test_compile_no_log_yields_none_pages(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=None))
    result = comp.compile(tex, out_dir=tmp_path)
    assert result["page_count"] is None
    assert result["ok"] is False


def test_uses_last_page_count_in_log(tmp_path):
    tex = _tex(tmp_path)

    def runner(cmd, **kwargs):
        (tmp_path / f"{tex.stem}.log").write_text(
            "Output written on paper.pdf (3 pages, 1 bytes).\n"
            "Output written on paper.pdf (15 pages, 9 bytes).\n",
            encoding="utf-8",
        )
        (tmp_path / f"{tex.stem}.pdf").write_bytes(b"%PDF")
        return _FakeProc()

    comp = LatexCompiler(runner=runner)
    assert comp.compile(tex, out_dir=tmp_path)["page_count"] == 15


def test_verify_pass(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=15))
    result = comp.verify(tex, 14, 16, out_dir=tmp_path)
    assert result["status"] == "PASS"
    assert result["within_target"] is True
    assert result["target"] == (14, 16)


def test_verify_short(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=9))
    result = comp.verify(tex, 14, 16, out_dir=tmp_path)
    assert result["status"] == "SHORT"
    assert result["within_target"] is False


def test_verify_over(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=40))
    result = comp.verify(tex, 14, 16, out_dir=tmp_path)
    assert result["status"] == "OVER"


def test_verify_compile_failed(tmp_path):
    tex = _tex(tmp_path)
    comp = LatexCompiler(runner=_make_runner(tmp_path, tex.stem, pages=None))
    result = comp.verify(tex, 14, 16, out_dir=tmp_path)
    assert result["status"] == "COMPILE_FAILED"
    assert result["within_target"] is False
