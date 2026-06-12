import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.latex_style import CoverInfo, cover_page_tex, enhanced_preamble, load_cover_info


def _write_cfg(tmp_path, data):
    p = tmp_path / "setup.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_load_cover_info_reads_all_fields(tmp_path):
    cfg = _write_cfg(
        tmp_path,
        {
            "cover_page": {
                "subject": "TestSubject",
                "authors": "Author A",
                "date": "2026",
                "course": "Course X",
                "lecturer": "Prof Y",
            }
        },
    )
    info = load_cover_info(cfg)
    assert info.subject == "TestSubject"
    assert info.authors == "Author A"
    assert info.date == "2026"
    assert info.course == "Course X"
    assert info.lecturer == "Prof Y"


def test_load_cover_info_subject_fallback(tmp_path):
    cfg = _write_cfg(tmp_path, {"paper_generation": {"subject": "FallbackSubject"}})
    info = load_cover_info(cfg)
    assert info.subject == "FallbackSubject"


def test_load_cover_info_empty_when_no_keys(tmp_path):
    cfg = _write_cfg(tmp_path, {})
    info = load_cover_info(cfg)
    assert info.subject == ""
    assert info.authors == ""
    assert info.course == ""


def test_enhanced_preamble_adds_fancyhdr():
    info = CoverInfo(subject="S", authors="A", date="D", course="C", lecturer="L")
    result = enhanced_preamble("preamble\n\\begin{document}\n", info)
    assert "fancyhdr" in result
    assert "\\pagestyle{fancy}" in result


def test_enhanced_preamble_preserves_begin_document():
    info = CoverInfo(subject="S", authors="A", date="D", course="C", lecturer="L")
    result = enhanced_preamble("preamble\n\\begin{document}\n", info)
    assert "\\begin{document}" in result


def test_enhanced_preamble_injects_before_begin_document():
    info = CoverInfo(subject="Subj", authors="A", date="D", course="C", lecturer="L")
    base = "preamble\n\\begin{document}\n"
    result = enhanced_preamble(base, info)
    fancyhdr_pos = result.find("fancyhdr")
    begin_pos = result.find("\\begin{document}")
    assert fancyhdr_pos < begin_pos


def test_enhanced_preamble_escapes_subject_special_chars():
    info = CoverInfo(subject="50% Off & More", authors="", date="", course="", lecturer="")
    result = enhanced_preamble("\\begin{document}\n", info)
    assert "\\%" in result
    assert "\\&" in result


def test_cover_page_tex_has_titlepage_env():
    info = CoverInfo(subject="S", authors="A", date="D", course="C", lecturer="L")
    tex = cover_page_tex(info)
    assert "\\begin{titlepage}" in tex
    assert "\\end{titlepage}" in tex


def test_cover_page_tex_contains_all_fields():
    info = CoverInfo(
        subject="SubjectX",
        authors="AuthorY",
        date="DateZ",
        course="CourseW",
        lecturer="LecturerV",
    )
    tex = cover_page_tex(info)
    assert "SubjectX" in tex
    assert "AuthorY" in tex
    assert "DateZ" in tex
    assert "CourseW" in tex
    assert "LecturerV" in tex


def test_cover_page_tex_has_newpage():
    info = CoverInfo(subject="S", authors="A", date="D", course="C", lecturer="L")
    tex = cover_page_tex(info)
    assert "\\newpage" in tex
