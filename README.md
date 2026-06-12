# Autonomous Academic Paper Generation Pipeline

An AI pipeline that autonomously researches a topic, writes a Hebrew academic paper, and compiles it to a print-ready PDF — end-to-end, without manual writing.

> **Output length note:** The pipeline currently produces papers of approximately **20 pages**. The Gemini free-tier enforces strict rate limits (20 requests/day, 1 M tokens/minute), which causes the writer agent to stay conservative rather than risk mid-generation quota exhaustion. Upgrading to a paid Gemini API key and raising `max_requests_per_minute` in `config/rate_limits.json` will unlock longer output.

---

## Project Overview

The pipeline accepts a topic and a folder of source PDFs, then produces a fully typeset PDF through five autonomous stages:

1. **Corpus Ingestion** — source PDFs are chunked and indexed into a local ChromaDB vector store using `gemini-embedding-001` (768-dimensional embeddings).
2. **Research** — a Researcher agent queries the vector store via RAG to extract citation-backed facts, rejecting any claim below a 0.72 cosine-similarity threshold.
3. **Writing** — a Writer agent drafts a structured academic paper in Hebrew using only the verified research facts.
4. **Review** — a Reviewer agent audits the draft for academic tone, structural coherence, and zero hallucinations, tracing every claim to a source citation.
5. **LaTeX Structuring** — a LaTeX agent injects mandatory elements (TOC, figures, data tables, the Drake Equation) and writes the final Markdown draft.

After generation the pipeline converts the draft to LuaLaTeX, runs a 4-pass compilation (LuaLaTeX → Biber → LuaLaTeX → LuaLaTeX), and pauses at a **Human-in-the-Loop gate** for manual sign-off before archiving the final PDF.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          run_pipeline.py                            │
│                    (entry point / CLI wrapper)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                     PaperOrchestrator
                    (sdk/core.py — CrewAI)
                             │
          ┌──────────────────┼──────────────────────┐
          │                  │                       │
   ResearcherAgent    WriterAgent           ReviewerAgent
   (RAG search)       (Hebrew draft)        (hallucination audit)
          │                  │                       │
          └──────────────────┴──────────────────────┘
                             │
                       LaTeXAgent
                  (structure + placeholders)
                             │
                      output.md  ◄──── data/processed/
                             │
                  LatexConverter (sdk/latex_converter.py)
                  + latex_style  (cover page, fancyhdr)
                  + asset_generator (matplotlib figures)
                             │
                      output.tex
                             │
                  LatexCompiler (sdk/latex_compiler.py)
                  4-pass: lualatex → biber → lualatex × 2
                             │
                      build/output.pdf
                             │
                  HumanInLoopGate (sdk/hil_gate.py)
                  Manual sign-off on 4 review items
                             │
                     ✓  Final PDF
```

### Agent–Skill mapping

Each agent loads a Markdown skill file from `skills/` at startup. The skill file shapes the agent's persona, constraints, and output format.

| Agent | Class | Skill file |
|-------|-------|-----------|
| Researcher | `ResearcherAgent` | `skills/research_skill.md` |
| Writer | `WriterAgent` | `skills/writing_skill.md` |
| Reviewer | `ReviewerAgent` | `skills/review_skill.md` |
| LaTeX | `LaTeXAgent` | `skills/latex_skill.md` |

### Key modules

| Module | Responsibility |
|--------|----------------|
| `sdk/pipeline.py` | Top-level orchestration: ingestion → generation → HIL gate |
| `sdk/core.py` | Builds the CrewAI crew and task graph |
| `sdk/token_economy.py` | Pricing matrices, token extraction from CrewAI results, cost computation, and page-count extrapolation model |
| `sdk/latex_converter.py` | Markdown → LuaLaTeX conversion |
| `sdk/latex_compiler.py` | 4-pass latexmk compile |
| `sdk/latex_style.py` | Cover page + fancyhdr preamble |
| `sdk/asset_generator.py` | Generates matplotlib figures (star field, UAP chart, belief-network diagram) |
| `tools/rag_core.py` | ChromaDB vector store wrapper |
| `tools/rag_query.py` | Embedding-based similarity search |
| `sdk/ingest.py` | PDF → chunks → ChromaDB |
| `sdk/hil_gate.py` | Human-in-the-Loop sign-off gate |
| `sdk/bib_sync.py` | Synchronises in-text citation numbers to `references.bib` |
| `sdk/corpus_bib.py` | Extracts bibliographic records from corpus PDFs for citation fallback |
| `sdk/post_generation.py` | Bibliography synchronization and PDF page-length verification |
| `tools/web_search.py` | Academic web search (via the `ddgs` DuckDuckGo client) for the Researcher agent |
| `sdk/web_sources.py` | Persists the researcher's web hits so real online URLs land in `references.bib` |

---

## Installation

### Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** (recommended) or pip
- **MiKTeX 25+** with LuaLaTeX engine
  - After installing, open **MiKTeX Console → Packages** and install: `latexmk`, `babel-hebrew`, `fontspec`, `biblatex`, `biber`, `fancyhdr`, `float`, `graphicx`
  - Enable on-the-fly package installation in MiKTeX Console → Settings
- **A Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey)

### Setup with uv (recommended)

```bash
# 1. Clone the repo
git clone <repo-url>
cd <repo-directory>

# 2. Create a virtual environment and install all dependencies in one step
uv sync

# Alternatively, install including dev tools (pytest, ruff):
uv sync --extra dev
```

`uv sync` reads `pyproject.toml`, creates `.venv/` automatically, and installs the pinned dependency graph — no separate `venv` or `pip install` step needed.

### Setup with pip (alternative)

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Configure credentials

```bash
cp .env-example .env
# Edit .env and set your GEMINI_API_KEY
```

---

## Usage

### Quick start

```bash
# 1. Drop your source PDFs into data/raw/ (these become the RAG corpus)
#    At least one PDF is required.

# 2. First run — ingests the corpus, generates the paper, compiles PDF, opens HIL gate
uv run python run_pipeline.py

# 3. Subsequent runs — corpus is already indexed, skip re-ingestion
uv run python run_pipeline.py --skip-ingestion
```

Every run compiles the PDF and saves a recompilable snapshot (`output.pdf` + `output.tex` + `references.bib`) into a timestamped folder under `data/processed/articles/`.

> **Be patient — a full run takes ~5 minutes.** The bulk of that time is spent waiting on the Gemini API: the four agents (Researcher → Writer → Reviewer → LaTeX) each make sequential calls, and free-tier Gemini responses are slow. The pipeline is working even when the console looks idle between log lines — don't interrupt it. (Transient `429`/`503` spikes are retried automatically with backoff, which can extend a run further.)

### CLI flags

| Flag | Effect |
|------|--------|
| *(none)* | Full run: ingest corpus → generate draft → compile PDF → HIL gate |
| `--skip-ingestion` | Skip corpus ingestion (use after the first run) |
| `--auto-approve-hil` | Bypass the interactive HIL gate (CI / automated runs) |
| `--verify-length` | After compiling, confirm the page count is within the configured target range |

**HIL gate:** after draft generation the pipeline pauses and asks you to approve four review items in the terminal. Read the compiled `.tex` (or open `data/processed/build/output.pdf`) before answering. Use `--auto-approve-hil` or set `HIL_AUTO_APPROVE=true` in your environment to skip it.

**Most common invocations:**

```bash
# Interactive run from the second run onwards
uv run python run_pipeline.py --skip-ingestion

# Fully automated / CI
uv run python run_pipeline.py --skip-ingestion --auto-approve-hil --verify-length
```

### SDK usage

```python
import logging
from dotenv import load_dotenv
from sdk.pipeline import run_pipeline

load_dotenv()
logging.basicConfig(level=logging.INFO)

outcome = run_pipeline(
    auto_approve_hil=True,   # skip interactive gate
    skip_ingestion=True,     # corpus already indexed
    verify_length=True,      # also check page count after compiling
)

print("Draft:    ", outcome["output_path"])   # data/processed/output.md
print("LaTeX:    ", outcome["tex_path"])      # data/processed/output.tex
print("Archived: ", outcome["archived_pdf"])  # data/processed/articles/paper_.../output.pdf
print("Approved: ", outcome["approval"]["approved"])

if "length_report" in outcome:
    r = outcome["length_report"]
    print(f"Pages: {r['page_count']}  Status: {r['status']}")
```

For lower-level access, orchestrate the agents manually:

```python
from sdk.core import PaperOrchestrator

orchestrator = PaperOrchestrator(config_path="config/setup.json")
result = orchestrator.run()   # returns the CrewAI result object
```

### Output files

| Path | Description |
|------|-------------|
| `data/processed/output.md` | Raw Markdown draft from the agent crew |
| `data/processed/output.tex` | LuaLaTeX source (auto-generated; do not edit by hand) |
| `data/processed/build/output.pdf` | Final compiled PDF |
| `data/processed/references.bib` | BibTeX bibliography (auto-synced from draft) |
| `data/processed/assets/` | Generated figures: `star_field.pdf`, `uap_distribution.pdf`, `belief_network.pdf` |
| `data/processed/articles/` | Accumulated recompilable snapshots — one `paper_YYYYMMDD_HHMMSS/` folder per run, each containing `output.pdf`, `output.tex`, `references.bib` |

---

## Configuration Guide

All runtime behaviour is controlled by two JSON files and four Markdown skill files. No code changes are needed for common customisations.

### `config/setup.json`

Controls the LLM models, RAG retrieval parameters, paper generation target, and the cover page.

```jsonc
{
  "models": {
    "drafting":   "gemini-2.5-flash",   // LLM used by Researcher, Writer, LaTeX agents
    "reviewing":  "gemini-2.5-flash",   // LLM used by Reviewer agent
    "embedding":  "gemini-embedding-001", // Embedding model for RAG indexing and search
    "embedding_dimension": 768          // Must match the embedding model's output size
  },
  "rag_engine": {
    "chunk_size":           1000,   // Characters per text chunk during ingestion
    "chunk_overlap":         100,   // Overlap between adjacent chunks
    "top_k_retrieval":         5,   // Number of chunks returned per RAG query
    "similarity_threshold":  0.6    // Minimum cosine similarity to return a chunk
  },
  "paper_generation": {
    "target_pages_min": 25,         // Lower bound for draft length (informational)
    "target_pages_max": 30,         // Upper bound for draft length (informational)
    "verify_pages_min": 14,         // Lower bound used when --verify-length is passed
    "verify_pages_max": 16,         // Upper bound used when --verify-length is passed
    "language": "Hebrew",           // Draft language passed to the Writer agent
    "subject": "Extraterrestrials and Conspiracy Theories"
  },
  "cover_page": {
    "subject":  "חייזרים ותיאוריות קונספירציה",  // Displayed on the title page (Hebrew)
    "authors":  "Your Name",
    "date":     "יוני 2026",
    "course":   "----",       // ← fill in before submission
    "lecturer": "----"      // ← fill in before submission
  }
}
```

**Common tweaks:**
- Change `subject` in `paper_generation` to generate a paper on a different topic.
- Increase `top_k_retrieval` (e.g. to `8`) if the Researcher misses relevant sources.
- Raise `similarity_threshold` (e.g. to `0.72`) for stricter hallucination prevention.

### `config/rate_limits.json`

Controls how aggressively the pipeline calls the Gemini API and the vector DB.

```jsonc
{
  "llm_api": {
    "max_requests_per_minute": 60,  // Requests per minute to Gemini
    "max_tokens_per_minute": 1000000,
    "timeout_seconds": 90,          // Per-request timeout
    "max_retries": 5,               // Retry attempts on 429/503 errors
    "backoff_factor": 2.0           // Exponential backoff multiplier
  },
  "vector_db": {
    "max_concurrent_queries": 10,
    "timeout_seconds": 30
  }
}
```

**Common tweaks:**
- If you hit `429 RESOURCE_EXHAUSTED` errors, lower `max_requests_per_minute` to `30` and raise `max_retries` to `8`.
- If network latency is high, increase `timeout_seconds` to `120`.

**Rate limits and output length:** The Gemini free tier caps the pipeline at 20 generation requests/day. Within a single run the 4 agents each consume one request; there is no quota risk mid-generation. However, the model has been observed to keep drafts conservative (≈20 pages) when operating on a free-tier key. Switching to a paid API key removes this behavioural constraint.

**Token usage tracking:** After every pipeline run, aggregate token counts (prompt tokens, completion tokens, total tokens, and successful requests) are read from the CrewAI result object and stored in the `Harness` token registry via `sdk/token_economy.py::extract_crew_token_usage()`. Cost is computed against the pricing matrices in `PRICING` and logged at INFO level. See `docs/token_economy_report.md` for the full cost analysis of the reference run (estimated grand total: **$0.026** for a 20-page paper).

### Agent skill files (`skills/*.md`)

Each agent's behaviour, persona, and hard constraints are defined in a Markdown file loaded at runtime. Editing a skill file is the primary way to change how an agent reasons or formats its output — no Python changes required.

| File | Controls |
|------|----------|
| `skills/research_skill.md` | Fact-extraction protocol, RAG similarity threshold (default 0.72), anti-hallucination rules, citation format |
| `skills/writing_skill.md` | Draft structure, section ordering, writing tone, Hebrew style guide |
| `skills/review_skill.md` | Audit checklist, acceptance criteria for academic tone and citation completeness |
| `skills/latex_skill.md` | Rules for injecting structural placeholders (`[TOC]`, `[IMAGE ...]`, `[DATA GRAPH ...]`, etc.) |

**Example — raise the RAG acceptance threshold in `research_skill.md`:**

Find the line:
```
Only chunks with similarity score $\ge 0.72$ should be accepted.
```
Change `0.72` to `0.80` for stricter sourcing. The Researcher agent will then reject more chunks as insufficiently relevant.

**Example — change the writing language:**

In `config/setup.json` set `"language": "English"`. The Writer agent's task prompt is constructed from this value, so the draft will switch to English without any code change.

---

## Running Tests

```bash
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

Coverage target: ≥85% per module. All modules currently meet this requirement.

## Linting

```bash
uv run ruff check src/ tests/
```

Line length limit: 115 characters (configured in `pyproject.toml`).
