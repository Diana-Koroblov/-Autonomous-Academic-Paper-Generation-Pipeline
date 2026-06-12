# Dependencies

## System Software

| Software | Version (tested) | Purpose | Install |
|----------|-----------------|---------|---------|
| Python | 3.11.9 | Runtime | [python.org](https://www.python.org/downloads/) |
| MiKTeX | 25.12 | LaTeX distribution (LuaLaTeX + latexmk) | [miktex.org](https://miktex.org/download) |

### MiKTeX packages required

After installing MiKTeX, open **MiKTeX Console** → **Packages** and install:

- `latexmk` — 4-pass compilation orchestrator
- `babel-hebrew` — Hebrew bidirectional text support
- `fontspec` — custom font loading (Arial)
- `biblatex`, `biber` — bibliography management
- `fancyhdr` — header/footer styling
- `float` — `[H]` figure placement
- `graphicx` — `\includegraphics` support

MiKTeX can also install missing packages automatically on first compile (on-the-fly install must be enabled in MiKTeX Console settings).

---

## Python Packages

### Runtime (required to run the pipeline)

| Package | Version (tested) | Purpose |
|---------|-----------------|---------|
| `crewai` | 1.14.6 | Multi-agent orchestration framework |
| `chromadb` | 1.1.1 | Local vector database (RAG) |
| `google-genai` | 2.8.0 | Gemini API client (LLM + embeddings) |
| `pymupdf` | 1.27.2.3 | PDF parsing for corpus ingestion |
| `matplotlib` | 3.10.7 | Python-generated data graph + diagram figures |
| `numpy` | 2.2.6 | Numerical arrays for figure generation |
| `python-bidi` | 0.6.10 | Hebrew right-to-left text rendering in matplotlib diagrams |
| `python-dotenv` | 1.2.2 | `.env` file loading for API credentials |

### Development (required to run tests and linting)

| Package | Version (tested) | Purpose |
|---------|-----------------|---------|
| `pytest` | 9.0.3 | Unit test runner |
| `pytest-cov` | — | Code coverage reporting |
| `ruff` | — | Linter and formatter |

Install all packages:
```powershell
pip install -e ".[dev]"
```

---

## API Credentials

| Credential | Where to get it | Where to put it |
|------------|----------------|-----------------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) | `.env` file (copy from `.env-example`) |

The pipeline uses:
- **Model**: `gemini-2.5-flash` for text generation
- **Embeddings**: `gemini-embedding-001` (768-dimensional vectors)

---

## Notes

- The `.venv/` directory is not portable — recreate it on each machine with `pip install -e ".[dev]"`.
- `crewai` releases frequently and may introduce breaking changes. If the pipeline breaks after a fresh install, pin the version in `pyproject.toml` to `crewai==1.14.6`.
- The ChromaDB vector store (`data/processed/chroma_db/`) is checked into the repo, so re-ingestion is only needed if you add new source PDFs to `data/raw/`.
- The matplotlib belief-network diagram needs a Hebrew-capable font (Arial on Windows, or Noto Sans Hebrew / FreeSans on Linux). If none is found, Hebrew labels render as empty boxes.
