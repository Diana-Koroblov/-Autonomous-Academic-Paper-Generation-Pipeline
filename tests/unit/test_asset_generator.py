import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pathlib import Path

from sdk.asset_generator import generate_all, generate_star_field, generate_uap_distribution


def test_generate_star_field_creates_file(tmp_path):
    out = generate_star_field(tmp_path / "star_field.pdf")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_generate_star_field_returns_path(tmp_path):
    out = generate_star_field(tmp_path / "star_field.pdf")
    assert isinstance(out, Path)
    assert out.name == "star_field.pdf"


def test_generate_uap_distribution_creates_file(tmp_path):
    out = generate_uap_distribution(tmp_path / "uap.pdf")
    assert out.exists()
    assert out.stat().st_size > 500


def test_generate_uap_distribution_returns_path(tmp_path):
    out = generate_uap_distribution(tmp_path / "uap.pdf")
    assert isinstance(out, Path)
    assert out.name == "uap.pdf"


def test_generate_all_creates_both_files(tmp_path):
    result = generate_all(tmp_path / "assets")
    assert result["star_field"].exists()
    assert result["uap_distribution"].exists()


def test_generate_all_creates_asset_dir(tmp_path):
    asset_dir = tmp_path / "assets"
    assert not asset_dir.exists()
    generate_all(asset_dir)
    assert asset_dir.is_dir()


def test_generate_all_returns_two_paths(tmp_path):
    result = generate_all(tmp_path)
    assert set(result.keys()) == {"star_field", "uap_distribution"}
    for p in result.values():
        assert isinstance(p, Path)


def test_generate_star_field_creates_parent_dirs(tmp_path):
    nested = tmp_path / "a" / "b" / "star_field.pdf"
    generate_star_field(nested)
    assert nested.exists()
