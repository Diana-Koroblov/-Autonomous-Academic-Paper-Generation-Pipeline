"""
Token economy utilities: pricing matrices, cost computation, CrewAI token
extraction, and budget projection for the autonomous paper pipeline.
"""
from typing import Any, Dict, Optional

# USD per million tokens (official Google AI Studio / Gemini API pricing, June 2026)
PRICING: Dict[str, Dict[str, float]] = {
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    # litellm resolves gemini/gemini-2.5-flash → gemini-2.5-flash-lite at runtime
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-embedding-001": {"input": 0.025, "output": 0.0},
}


def compute_cost(model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
    """Returns per-component and total USD cost for a single model call."""
    rates = PRICING.get(model, PRICING["gemini-2.5-flash"])
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
    }


def extract_crew_token_usage(result: Any) -> Optional[Dict[str, int]]:
    """
    Reads aggregate token counts from a CrewAI CrewOutput object.
    Returns None when the result carries no UsageMetrics (e.g. older builds).
    """
    token_usage = getattr(result, "token_usage", None)
    if token_usage is None:
        return None
    return {
        "input_tokens": getattr(token_usage, "prompt_tokens", 0),
        "output_tokens": getattr(token_usage, "completion_tokens", 0),
        "total_tokens": getattr(token_usage, "total_tokens", 0),
        "successful_requests": getattr(token_usage, "successful_requests", 0),
    }


def compute_pipeline_cost(
    input_tokens: int,
    output_tokens: int,
    embedding_tokens: int = 0,
    gen_model: str = "gemini-2.5-flash-lite",
    embedding_model: str = "gemini-embedding-001",
) -> Dict[str, Any]:
    """
    Aggregates generation + embedding costs into a single pipeline cost report.
    """
    gen = compute_cost(gen_model, input_tokens, output_tokens)
    emb = compute_cost(embedding_model, embedding_tokens, 0)
    return {
        "generation": gen,
        "embedding": emb,
        "grand_total_usd": round(gen["total_cost_usd"] + emb["total_cost_usd"], 6),
        "gen_model": gen_model,
        "embedding_model": embedding_model,
        "token_summary": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "embedding_tokens": embedding_tokens,
            "total_tokens": input_tokens + output_tokens + embedding_tokens,
        },
    }


def extrapolate_cost(
    base_pages: int,
    base_cost_usd: float,
    target_pages: int,
    gen_model: str = "gemini-2.5-flash-lite",
) -> Dict[str, Any]:
    """
    Linear page-count extrapolation: cost scales proportionally with document
    length (more pages ≈ larger reviewer/LaTeX context windows).
    """
    scale = target_pages / max(base_pages, 1)
    rates = PRICING.get(gen_model, PRICING["gemini-2.5-flash"])
    return {
        "base_pages": base_pages,
        "target_pages": target_pages,
        "scale_factor": round(scale, 3),
        "estimated_cost_usd": round(base_cost_usd * scale, 6),
        "model": gen_model,
        "pricing_note": (
            f"Input ${rates['input']:.3f}/M tokens, "
            f"Output ${rates['output']:.3f}/M tokens"
        ),
    }
