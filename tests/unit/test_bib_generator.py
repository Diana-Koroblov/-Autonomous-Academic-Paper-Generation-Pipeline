import os
import sys

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.bib_generator import extract_cite_keys, generate_bib, key_to_entry

TEX = r"""
\cite{von_daniken_chariots_1970}
Some text \parencite{festinger_theory_1957, pariser_filter_2011}.
Repeat \cite{von_daniken_chariots_1970} and \textcite{usaf_historical_study_195}.
"""


def test_extract_cite_keys_dedup_and_sorted():
    keys = extract_cite_keys(TEX)
    assert keys == [
        "festinger_theory_1957",
        "pariser_filter_2011",
        "usaf_historical_study_195",
        "von_daniken_chariots_1970",
    ]


def test_extract_cite_keys_empty():
    assert extract_cite_keys("no citations here") == []


def test_key_to_entry_parses_author_title_year():
    entry = key_to_entry("von_daniken_chariots_1970")
    assert "@book{von_daniken_chariots_1970," in entry
    assert "author = {Von}" in entry
    assert "title  = {Daniken Chariots}" in entry
    assert "year   = {1970}" in entry


def test_key_to_entry_no_year():
    entry = key_to_entry("smith_orientalism")
    assert "year   = {n.d.}" in entry
    assert "author = {Smith}" in entry


def test_key_to_entry_short_numeric_year():
    entry = key_to_entry("usaf_historical_study_195")
    assert "year   = {195}" in entry


def test_generate_bib_writes_entries(tmp_path):
    tex = tmp_path / "doc.tex"
    bib = tmp_path / "references.bib"
    tex.write_text(TEX, encoding="utf-8")

    count = generate_bib(tex, bib)
    assert count == 4
    content = bib.read_text(encoding="utf-8")
    assert content.count("@book{") == 4
    assert "not RAG-verified" in content


def test_generate_bib_no_keys(tmp_path):
    tex = tmp_path / "doc.tex"
    bib = tmp_path / "references.bib"
    tex.write_text("plain text", encoding="utf-8")
    assert generate_bib(tex, bib) == 0
    assert not bib.exists()
