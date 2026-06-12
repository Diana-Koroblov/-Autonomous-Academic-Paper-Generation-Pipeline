import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from sdk.token_economy import (
    PRICING,
    compute_cost,
    compute_pipeline_cost,
    extract_crew_token_usage,
    extrapolate_cost,
)


# ---------------------------------------------------------------------------
# compute_cost
# ---------------------------------------------------------------------------

def test_compute_cost_known_model():
    r = compute_cost("gemini-2.5-flash-lite", 1_000_000, 1_000_000)
    assert r["input_cost_usd"] == 0.10
    assert r["output_cost_usd"] == 0.40
    assert r["total_cost_usd"] == 0.50


def test_compute_cost_zero_tokens():
    r = compute_cost("gemini-2.5-flash", 0, 0)
    assert r["total_cost_usd"] == 0.0


def test_compute_cost_unknown_model_falls_back_to_flash():
    r = compute_cost("unknown-model", 1_000_000, 0)
    assert r["input_cost_usd"] == PRICING["gemini-2.5-flash"]["input"]


def test_compute_cost_embedding_model_no_output_cost():
    r = compute_cost("gemini-embedding-001", 1_000_000, 0)
    assert r["output_cost_usd"] == 0.0
    assert r["input_cost_usd"] == pytest_approx(0.025)


def test_compute_cost_pro_model():
    r = compute_cost("gemini-2.5-pro", 200_000, 10_000)
    assert r["input_cost_usd"] == pytest_approx(0.25)
    assert r["output_cost_usd"] == pytest_approx(0.10)


# ---------------------------------------------------------------------------
# extract_crew_token_usage
# ---------------------------------------------------------------------------

def test_extract_crew_token_usage_returns_none_when_no_attribute():
    result = SimpleNamespace()  # no token_usage attribute
    assert extract_crew_token_usage(result) is None


def test_extract_crew_token_usage_returns_none_when_attribute_is_none():
    result = SimpleNamespace(token_usage=None)
    assert extract_crew_token_usage(result) is None


def test_extract_crew_token_usage_reads_metrics():
    usage = SimpleNamespace(prompt_tokens=100, completion_tokens=200, total_tokens=300, successful_requests=4)
    result = SimpleNamespace(token_usage=usage)
    out = extract_crew_token_usage(result)
    assert out == {"input_tokens": 100, "output_tokens": 200, "total_tokens": 300, "successful_requests": 4}


def test_extract_crew_token_usage_defaults_missing_fields():
    usage = SimpleNamespace()  # no sub-fields
    result = SimpleNamespace(token_usage=usage)
    out = extract_crew_token_usage(result)
    assert out == {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "successful_requests": 0}


# ---------------------------------------------------------------------------
# compute_pipeline_cost
# ---------------------------------------------------------------------------

def test_compute_pipeline_cost_grand_total():
    r = compute_pipeline_cost(42_000, 48_000, 106_000)
    assert r["grand_total_usd"] > 0
    assert "generation" in r
    assert "embedding" in r


def test_compute_pipeline_cost_no_embedding():
    r = compute_pipeline_cost(1_000_000, 1_000_000, 0)
    assert r["embedding"]["total_cost_usd"] == 0.0
    assert r["grand_total_usd"] == r["generation"]["total_cost_usd"]


def test_compute_pipeline_cost_token_summary():
    r = compute_pipeline_cost(10, 20, 5)
    s = r["token_summary"]
    assert s["input_tokens"] == 10
    assert s["output_tokens"] == 20
    assert s["embedding_tokens"] == 5
    assert s["total_tokens"] == 35


def test_compute_pipeline_cost_records_model_names():
    r = compute_pipeline_cost(0, 0, 0, gen_model="gemini-2.5-pro")
    assert r["gen_model"] == "gemini-2.5-pro"


# ---------------------------------------------------------------------------
# extrapolate_cost
# ---------------------------------------------------------------------------

def test_extrapolate_cost_same_pages_returns_base():
    r = extrapolate_cost(20, 0.026, 20)
    assert r["estimated_cost_usd"] == pytest_approx(0.026)
    assert r["scale_factor"] == 1.0


def test_extrapolate_cost_doubles_at_double_pages():
    r = extrapolate_cost(20, 0.026, 40)
    assert r["estimated_cost_usd"] == pytest_approx(0.052)
    assert r["scale_factor"] == 2.0


def test_extrapolate_cost_returns_metadata():
    r = extrapolate_cost(20, 0.026, 30, gen_model="gemini-2.5-flash")
    assert r["base_pages"] == 20
    assert r["target_pages"] == 30
    assert r["model"] == "gemini-2.5-flash"
    assert "pricing_note" in r


def test_extrapolate_cost_zero_base_pages_does_not_divide_by_zero():
    r = extrapolate_cost(0, 0.026, 30)
    assert r["scale_factor"] == pytest_approx(30.0)


# ---------------------------------------------------------------------------
# helper: approximate equality (avoids importing pytest at module level)
# ---------------------------------------------------------------------------

def pytest_approx(val, rel=1e-4):
    import pytest
    return pytest.approx(val, rel=rel)
