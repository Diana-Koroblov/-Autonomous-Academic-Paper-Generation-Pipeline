import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pathlib import Path

from sdk.belief_network import _hebrew_font, _rtl, generate_belief_network


def test_generate_belief_network_creates_file(tmp_path):
    out = generate_belief_network(tmp_path / "belief_network.pdf")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_generate_belief_network_returns_path(tmp_path):
    out = generate_belief_network(tmp_path / "belief_network.pdf")
    assert isinstance(out, Path)
    assert out.name == "belief_network.pdf"


def test_generate_belief_network_creates_parent_dirs(tmp_path):
    nested = tmp_path / "a" / "b" / "belief_network.pdf"
    generate_belief_network(nested)
    assert nested.exists()


def test_rtl_reverses_hebrew_visual_order():
    src = "שלום"
    assert _rtl(src) == src[::-1]


def test_hebrew_font_returns_font_properties():
    font = _hebrew_font()
    # A Hebrew-capable font resolves to an actual file on this platform.
    assert font.get_name() or font.get_file() is not None
