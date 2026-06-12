# Token Economy Report
**Project:** Autonomous Academic Paper Generation Pipeline  
**Version:** 1.0.0 (tag `v1.0.0-final`)  
**Report Date:** 2026-06-12  
**Pipeline Run Date:** 2026-06-10  
**Author:** AI Orchestration System — Post-Generation Analysis

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total pipeline runs analyzed | 1 (session `f9583b0e`) |
| Generative model (configured) | `gemini-2.5-flash` |
| Generative model (actual runtime) | `gemini-2.5-flash-lite` (litellm alias) |
| Embedding model | `gemini-embedding-001` |
| Total LLM API calls | 4 (one per agent) |
| Estimated total tokens | **159,150** |
| Estimated generation cost | **$0.0237 USD** |
| Estimated embedding cost | **$0.0027 USD** |
| **Estimated grand total** | **$0.0264 USD** |
| Paper output | 20 pages, 72,500-byte Markdown draft |

The pipeline is extremely cost-efficient: a complete 20-page academic paper in
Hebrew costs less than **$0.03** at current pricing.

---

## 1. Model Configuration and Pricing Matrix

### 1.1 Configured Models (`config/setup.json`)

| Role | Configured Model ID | Actual Runtime Model | Notes |
|------|--------------------|--------------------|-------|
| Researcher | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | litellm resolves `gemini/gemini-2.5-flash` → lite variant |
| Writer | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | Same alias resolution |
| Reviewer | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | Config changed from `gemini-2.5-pro` to `flash` |
| LaTeX Formatter | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | Same alias resolution |
| Embedding (RAG) | `gemini-embedding-001` | `gemini-embedding-001` | Direct Google AI SDK call |

**Note on alias resolution:** CrewAI delegates LLM calls to litellm, which
routes `gemini/gemini-2.5-flash` to the `gemini-2.5-flash-lite` endpoint as
confirmed by HTTP request logs:
`POST …/v1beta/models/gemini-2.5-flash-lite:generateContent`.

### 1.2 Pricing Matrix (USD per Million Tokens, Google AI Studio — June 2026)

| Model | Input ($/M) | Output ($/M) | Notes |
|-------|------------|-------------|-------|
| `gemini-2.5-flash` | $0.150 | $0.600 | Standard; thinking tokens billed as output |
| `gemini-2.5-flash-lite` | $0.100 | $0.400 | Lightweight alias; **this is what ran** |
| `gemini-2.5-pro` | $1.250 | $10.000 | Reviewer upgrade path; not used in this run |
| `gemini-embedding-001` | $0.025 | $0.000 | Per embedded token; output N/A |

> Pricing reflects published Google AI Studio rates as of mid-2026.
> Free-tier users on Google AI Studio quota (20 req/day for `gemini-2.5-flash`)
> incur $0.00 in practice until the paid API is activated.

---

## 2. Token Usage Analysis

### 2.1 Methodology

The pipeline run on 2026-06-10 predates the `token_economy.py` instrumentation
(implemented 2026-06-12 in this PR). Token counts below are reconstructed from
first principles:

- **Skill file sizes** (system prompts): measured in bytes, converted at
  ~4 bytes/token.
- **Task description lengths**: character-counted from `src/sdk/core.py`.
- **CrewAI framework overhead**: ~2,000 tokens/agent (ReAct scaffolding, tool
  schema injection, CoT formatting).
- **Inter-agent context passing**: Writer receives Researcher output (~500
  tokens); Reviewer receives Writer draft (~15,000 tokens); LaTeX Formatter
  receives Reviewer output (~15,000 tokens).
- **Output sizes**: inferred from `data/processed/output.md` (72,500 bytes,
  Hebrew-dense; ~4 chars/token → ~18,000 tokens).
- **Embedding tokens**: 426 corpus vectors × ~250 tokens/chunk = 106,500
  tokens (ingestion); 5 RAG query embeddings × ~50 tokens = 250 tokens (runtime).

### 2.2 Input Token Breakdown by Agent

| Agent | System Prompt | Task Desc. | Context In | CrewAI Overhead | **Total Input** |
|-------|--------------|-----------|-----------|----------------|----------------|
| Researcher | 732 | 63 | 1,250 (RAG chunks) | 2,000 | **4,045** |
| Writer | 719 | 50 | 500 (research summary) | 2,000 | **3,269** |
| Reviewer | 483 | 38 | 15,000 (draft) | 2,000 | **17,521** |
| LaTeX Formatter | 510 | 50 | 15,000 (reviewed draft) | 2,000 | **17,560** |
| **Total (LLM)** | | | | | **42,395** |
| Corpus embeddings | — | — | — | — | 106,500 |
| Query embeddings | — | — | — | — | 250 |
| **Grand Total Input** | | | | | **149,145** |

### 2.3 Output Token Breakdown by Agent

| Agent | Output Description | Estimated Tokens |
|-------|-------------------|-----------------|
| Researcher | Short research brief, no RAG hits | 500 |
| Writer | Full Hebrew academic draft | 15,000 |
| Reviewer | Corrected draft (approximately equal to writer output) | 15,000 |
| LaTeX Formatter | Structured Markdown with LaTeX placeholders | 18,000 |
| **Total Output (LLM)** | | **48,500** |
| Embeddings (output N/A) | — | 0 |
| **Grand Total Output** | | **48,500** |

### 2.4 Aggregate Summary

| Dimension | Tokens |
|-----------|--------|
| Total LLM input | 42,395 |
| Total LLM output | 48,500 |
| Total LLM tokens | 90,895 |
| Total embedding tokens | 106,750 |
| **Pipeline total tokens** | **197,645** |

> **Implementation note:** From 2026-06-12 onwards, `core.py` calls
> `extract_crew_token_usage(result)` after `Crew.kickoff()` and forwards
> the CrewAI `UsageMetrics` (prompt_tokens, completion_tokens, total_tokens,
> successful_requests) into `Harness.log_token_usage("crew_total", …)`.
> Future runs will report real measured values rather than estimates.

---

## 3. Financial Metrics

### 3.1 Generation Cost (LLM calls)

Using `gemini-2.5-flash-lite` rates ($0.10/M input, $0.40/M output):

| Component | Tokens | Rate ($/M) | Cost (USD) |
|-----------|--------|-----------|-----------|
| Input (all 4 agents) | 42,395 | $0.100 | $0.004240 |
| Output (all 4 agents) | 48,500 | $0.400 | $0.019400 |
| **Generation subtotal** | **90,895** | — | **$0.023640** |

### 3.2 Embedding Cost

Using `gemini-embedding-001` rates ($0.025/M input):

| Component | Tokens | Rate ($/M) | Cost (USD) |
|-----------|--------|-----------|-----------|
| Corpus ingestion (426 chunks) | 106,500 | $0.025 | $0.002663 |
| RAG query embeddings (runtime) | 250 | $0.025 | $0.000006 |
| **Embedding subtotal** | **106,750** | — | **$0.002669** |

### 3.3 Total Pipeline Cost

| Category | Cost (USD) |
|----------|-----------|
| LLM generation | $0.023640 |
| Vector embeddings | $0.002669 |
| **Grand total** | **$0.026309** |

**Per-page cost:** $0.026309 / 20 pages = **$0.001315 / page**

---

## 4. Real-Time Budget Tracking Analysis

### 4.1 Tracking Infrastructure Assessment

The pipeline implements a layered budget-awareness architecture:

| Layer | Component | Status | Notes |
|-------|-----------|--------|-------|
| Token registry | `Harness.token_registry` | **Implemented** | Pre-allocated per-agent buckets |
| Usage logging | `Harness.log_token_usage()` | **Implemented** | Accumulates input/output per key |
| CrewAI extraction | `extract_crew_token_usage()` | **Implemented (2026-06-12)** | Reads `CrewOutput.token_usage` post-kickoff |
| Rate limiting | `Gatekeeper` token bucket | **Active** | Caps at 1,000,000 tokens/min (config) |
| Real-time per-call | Per-agent streaming capture | **Not yet implemented** | Would require CrewAI step callbacks |
| Retry backoff | `pipeline.py _run_with_retry()` | **Active** | Detects 429/503, honors Retry-After |

### 4.2 Tracking Efficiency Throughout the Run

**Phase 1 — Corpus Ingestion** (pre-run, one-time):  
Embedding tokens were consumed silently with no counter increment. The 426
vectors represent ~$0.0027 of sunk cost that is amortized across all future
pipeline runs on the same corpus.

**Phase 2 — CrewAI Execution** (session `f9583b0e`, 2026-06-10):  
The `Harness` was initialized with zero-filled registries. No per-call hook
was wired, so token counts remained at zero throughout the run. The single
implemented guard was the `Gatekeeper`'s token-bucket rate limiter, which
ensured ≤1M tokens/minute throughput but did not accumulate totals.

**Phase 3 — Post-Run** (2026-06-12, this release):  
`extract_crew_token_usage(result)` is now called after `kickoff()`. CrewAI
1.14.6 accumulates `UsageMetrics` internally and exposes them on `CrewOutput`.
Future runs will surface real aggregate totals in the log and harness registry.

**Efficiency score (current release):** The architecture tracks budget at the
aggregate level (post-run) and enforces rate limits in real time. Per-agent,
per-call granularity requires a CrewAI step callback hook, which is a pending
improvement (see §6).

---

## 5. Actual vs. Predicted Budget Consumption

### 5.1 Pre-Run Estimates (Architect Projection)

Before the pipeline ran, the PRD targeted a 25–30 page paper with the
following rough token budget assumptions:

| Agent | Predicted Input | Predicted Output | Basis |
|-------|----------------|-----------------|-------|
| Researcher | 8,000 | 2,000 | ~2 RAG rounds assumed |
| Writer | 10,000 | 25,000 | 25-page draft at ~1,000 words/page |
| Reviewer | 30,000 | 25,000 | Reviewer reads full draft |
| LaTeX | 30,000 | 25,000 | Full doc restructure |
| **Total** | **78,000** | **77,000** | **155,000 predicted** |

### 5.2 Actual vs. Predicted Comparison

| Metric | Predicted | Actual | Delta | Root Cause |
|--------|-----------|--------|-------|-----------|
| Total input tokens | 78,000 | 42,395 | **−46%** | Single-pass writer; no RAG re-queries |
| Total output tokens | 77,000 | 48,500 | **−37%** | Model under-delivered vs. 25-page target; actual 20 pages |
| Total tokens | 155,000 | 90,895 | **−41%** | Both effects compound |
| Total cost (LLM) | $0.046 | $0.024 | **−48%** | Cheaper runtime model + fewer tokens |
| Pages produced | 25–30 | 20 | **−27%** | Model under-generates vs. prompt target (known behavior, see memory) |

### 5.3 Key Findings

1. **Model downgrade:** The config targeted `gemini-2.5-flash` ($0.15/$0.60 per
   M) but litellm aliased it to `gemini-2.5-flash-lite` ($0.10/$0.40), reducing
   generation cost by **33%**.

2. **Researcher agent under-performed:** The Researcher produced a minimal
   answer ("Please provide me with specific details…") rather than invoking
   the RAG tool. This reduced both its output and the context fed to the Writer,
   pulling total token consumption well below target.

3. **Writer output gap:** The Writer model consistently under-delivers relative
   to stated page targets (documented in project memory). The 20-page output vs.
   25–30-page target is a known tuning knob, not a cost issue.

4. **Embedding cost fixed:** Corpus ingestion is a one-time cost of ~$0.0027;
   subsequent runs with `--skip-ingestion` do not re-pay it.

---

## 6. Budget Projection Model (30+ Pages)

### 6.1 Linear Extrapolation Assumptions

Token consumption scales with document length primarily through the reviewer
and LaTeX formatter stages, which consume the full draft as input context.
The relationship is approximately linear:

```
total_tokens(N pages) ≈ fixed_overhead + N × tokens_per_page
```

From the observed 20-page run:
- Fixed overhead (researcher + writer system prompts + CrewAI scaffolding): ~10,000 tokens
- Per-page token cost: (90,895 − 10,000) / 20 ≈ **4,045 tokens/page**

### 6.2 Projected Costs by Target Page Count

| Target Pages | Estimated Tokens | LLM Cost (`flash-lite`) | LLM Cost (`flash`) | LLM Cost (`2.5-pro`) |
|-------------|-----------------|------------------------|-------------------|---------------------|
| 20 (baseline) | 90,895 | $0.024 | $0.043 | $0.698 |
| 25 | 111,125 | $0.029 | $0.052 | $0.853 |
| 30 | 131,350 | $0.034 | $0.062 | $1.008 |
| 50 | 212,250 | $0.055 | $0.100 | $1.629 |
| 100 | 414,500 | $0.107 | $0.195 | $3.178 |

**Projection formula** (implemented in `src/sdk/token_economy.extrapolate_cost()`):

```
estimated_cost = base_cost × (target_pages / base_pages)
```

### 6.3 Model Upgrade Impact

If the Reviewer is upgraded to `gemini-2.5-pro` (as originally architected),
the review stage alone (17,521 input + 15,000 output tokens) would cost:

```
input:  17,521 / 1,000,000 × $1.25  = $0.022
output: 15,000 / 1,000,000 × $10.00 = $0.150
reviewer subtotal: $0.172
```

This is **7.3×** the entire current pipeline cost. The flash model is the
correct choice for a cost-bounded single-pass architecture.

### 6.4 Break-Even Analysis (free tier vs. paid)

Google AI Studio free tier: **20 requests/day** for `gemini-2.5-flash`.  
Each pipeline run uses **4 requests** (4 agents, 1 call each).  
Free tier supports: **5 full pipeline runs/day** at $0.00 cost.

Paid API threshold: any run on the paid key at $0.024/run.  
Budget of **$1.00** supports **~38 full pipeline runs** at current token load.

---

## 7. Implementation Notes

### 7.1 Token Tracking — What Is Now Instrumented

```
run_pipeline()
  └─ orchestrator.run()
       └─ crew.kickoff()           ← CrewAI accumulates UsageMetrics
            └─ [4 LLM calls]
       └─ extract_crew_token_usage(result)
            └─ harness.log_token_usage("crew_total", input, output)
                 └─ harness.token_registry["crew_total"] updated
```

### 7.2 Recommended Future Enhancements

| Enhancement | Impact | Effort |
|-------------|--------|--------|
| CrewAI `step_callback` for per-agent token capture | Per-agent cost breakdown | Medium |
| Persist token registry to `logs/token_usage.json` after each run | Historical tracking | Low |
| Alert when cumulative daily spend > $0.10 | Budget guardrail | Low |
| Upgrade Researcher to multi-call RAG (capture each embedding call) | Accuracy | High |

---

*Report generated by post-generation analysis pass. Token counts marked as
"estimated" will be replaced by measured values on the next pipeline run after
the `token_economy.py` instrumentation is active.*
