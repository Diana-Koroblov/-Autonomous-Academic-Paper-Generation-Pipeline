# Project TODO List: Autonomous Academic Paper Generation Pipeline

## Global Mandate: Code Modularity & QA Protocol
Every Python (.py) file created or modified in this project is subject to a 3-step continuous refactoring and verification protocol:
1. **Implementation:** Write and implement the required logic fully.
2. **Size Verification & Refactoring:** Check the file length. If the logic causes the file to exceed 150 lines of code, pause and refactor by extracting components (e.g., functions, classes, mixins) into separate modules.
3. **Quality Assurance:** Enforce 0 Ruff violations and ensure >= 85% test coverage via `pytest-cov`.
*Note: Documentation (.md) and configuration files are exempt from this 3-step sequence.*

## Phase 1: Environment, Security & QA Infrastructure
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The environment is initialized with a robust security and QA posture. All foundational SDK files (Version, Gatekeeper, Harness) are implemented, verified under the 150-line limit, and pass the 0-Ruff/85%-coverage protocol. Configuration for rate limits and security is externalized.

### 1.1 Repository & Environment Genesis
- [X] 1.1.1 [Completed] [Architect] - Initialize workspace folder directory layout (`src/`, `tests/`, etc.) | DoD: All 8 operational paths physically exist on disk.
- [X] 1.1.2 [Completed] [Architect] - Configure `pyproject.toml` with strict Ruff metadata and `uv` dependencies | DoD: File passes syntax validation with no errors.
- [X] 1.1.3 [Completed] [Developer] - Execute `uv` to generate the deterministic `uv.lock` file | DoD: `uv.lock` successfully generated at project root.
- [X] 1.1.4 [Completed] [Developer] - Initialize testing paths (`tests/unit/`, `tests/integration/`) | DoD: Sub-directories created successfully.
- [X] 1.1.5 [Completed] [Developer] - Create `tests/conftest.py` for shared global testing fixtures | DoD: File exists and contains basic test fixtures.
- [X] 1.1.6 [Completed] [Architect] - Create standard secure `.gitignore` file to safeguard runtime caches | DoD: Git tracking successfully excludes target folders.
- [X] 1.1.7 [Completed] [Architect] - Create `.env-example` defining core LLM credential placeholders | DoD: File lists all required pipeline keys with dummy values.
- [X] 1.1.8 [Completed] [Architect] - Create `config/rate_limits.json` externalizing threshold matrices | DoD: Valid JSON file containing API bucket parameters is saved.
- [X] 1.1.9 [Completed] [Architect] - Create `config/setup.json` managing core app parameters | DoD: Valid JSON file mapping orchestrator environment configs is saved.

### 1.2 Shared Version Module
- [ ] 1.2.1 [Pending] [Developer] - Implement logic inside `src/shared/version.py` initializing version to `1.00` | DoD: File compiles and declares version variable string.
- [ ] 1.2.2 [Pending] [QA] - Verify line length limits for `version.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 1.2.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `version.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 1.3 SDK Gatekeeper Implementation
- [ ] 1.3.1 [Pending] [Developer] - Implement `src/sdk/gatekeeper.py` handling API rate limiting, exponential backoff retries, and strict FIFO Queue mechanism | DoD: File created with queue, retry, and limit logic.
- [ ] 1.3.2 [Pending] [QA] - Verify line length limits for `gatekeeper.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 1.3.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `gatekeeper.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 1.4 SDK Harness Implementation
- [ ] 1.4.1 [Pending] [Developer] - Implement `src/sdk/harness.py` to wrap agents for logging, context injection, and token tracking | DoD: File created with harness logging and tracking logic.
- [ ] 1.4.2 [Pending] [QA] - Verify line length limits for `harness.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 1.4.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `harness.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.
- [ ] 1.4.4 [Pending] [QA] - Finalize Phase 1 Post-Setup Compliance Audit | DoD: Official administrative validation and execution of **Gate 1** structural sign-off.

## Phase 2: RAG Engine & Specialized Documentation
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The RAG engine architecture is documented and implemented. Core retrieval, parsing, and querying modules are separated into distinct files, each verified under the 150-line limit and passing the full QA protocol.

### 2.1 RAG Architectural Documentation
- [ ] 2.1.1 [Pending] [Architect] - Write `docs/PRD_rag_engine.md` explicitly detailing the `text-embedding-3-small` model and exact 1000/100 chunking parameters | DoD: Markdown file exists and contains the exact parameter constraints.
- [ ] 2.1.2 [Pending] [Architect] - Place all source PDF documents regarding Extraterrestrials and Conspiracy Theories into the `data/` directory | DoD: PDFs successfully staged in `data/` directory.

### 2.2 RAG Core Module
- [ ] 2.2.1 [Pending] [Developer] - Implement `src/tools/rag_core.py` to manage base vector database connectivity | DoD: Database connection logic is fully implemented.
- [ ] 2.2.2 [Pending] [QA] - Verify line length limits for `rag_core.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 2.2.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `rag_core.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 2.3 RAG Parser Module
- [ ] 2.3.1 [Pending] [Developer] - Create `src/tools/rag_parser.py` for PDF extraction, strictly implementing 1000/100 chunking logic and extracting BibTeX metadata | DoD: Parser logic completes extraction with strict chunk boundaries and required metadata fields.
- [ ] 2.3.2 [Pending] [QA] - Verify line length limits for `rag_parser.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 2.3.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `rag_parser.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 2.4 RAG Query Module
- [ ] 2.4.1 [Pending] [Developer] - Implement Cosine Similarity mathematical retrieval ranking inside `src/tools/rag_query.py` | DoD: Script calculates exact vector dot product matching and strictly returns an empty context buffer if no chunk score satisfies the mandatory anti-hallucination threshold boundary of >= 0.72.
- [ ] 2.4.2 [Pending] [QA] - Verify line length limits for `rag_query.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 2.4.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `rag_query.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.
- [ ] 2.4.4 [Pending] [QA] - Validate RAG Ingestion Pipeline and Dynamic Skill Loader Core | DoD: Retrieval runtime confirmation matches targets (<1.5s) and formal execution of **Gate 2** sign-off.

## Phase 3: CrewAI Agent Intelligence & Skills Architecture
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The CrewAI team is deployed using the Skills pattern. Each agent (Researcher, Writer, Reviewer, LaTeX) is defined in a separate file, verified under the 150-line limit, and passing the full QA protocol. Explicit `SKILL.md` files guide agent behavior.

### 3.1 CrewAI Skills Repository
- [ ] 3.1.1 [Pending] [Architect] - Create the `skills/` directory at the project root | DoD: Directory physically exists on disk.
- [ ] 3.1.2 [Pending] [Architect] - Write `skills/research_skill.md`, explicitly defining that it must govern fact-cross-referencing and prevent memory poisoning | DoD: File created with strict instructions.
- [ ] 3.1.3 [Pending] [Architect] - Write `skills/writing_skill.md`, explicitly defining academic Hebrew prose style, structural coherence, and 25-30 page velocity | DoD: File created with strict constraints.
- [ ] 3.1.4 [Pending] [Architect] - Write `skills/review_skill.md`, explicitly mandating a strict truth-verification protocol against RAG chunks to eliminate hallucinations | DoD: File created with hallucination elimination rules.
- [ ] 3.1.5 [Pending] [Architect] - Write `skills/latex_skill.md`, explicitly governing accurate TikZ syntax compilation, math notation layout, and BiDi engine packages | DoD: File created with specific TeX constraints.

### 3.2 Researcher Agent Implementation
- [ ] 3.2.1 [Pending] [Developer] - Implement `src/agents/researcher.py` specializing in RAG-driven factual extraction, mandating programmatic SDK loading of skills | DoD: Agent dynamically rediscovers, activates, and injects its assigned skill via `pathlib.Path`.
- [ ] 3.2.2 [Pending] [QA] - Verify line length limits for `researcher.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 3.2.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `researcher.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 3.3 Writer Agent Implementation
- [ ] 3.3.1 [Pending] [Developer] - Implement `src/agents/writer.py` drafting academic Hebrew content, mandating programmatic SDK loading of skills | DoD: Agent dynamically rediscovers, activates, and injects its assigned skill via `pathlib.Path`.
- [ ] 3.3.2 [Pending] [QA] - Verify line length limits for `writer.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 3.3.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `writer.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 3.4 Reviewer Agent Implementation
- [ ] 3.4.1 [Pending] [Developer] - Implement `src/agents/reviewer.py` to perform fact-checking, mandating programmatic SDK loading of skills | DoD: Agent dynamically rediscovers, activates, and injects its assigned skill via `pathlib.Path`.
- [ ] 3.4.2 [Pending] [QA] - Verify line length limits for `reviewer.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 3.4.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `reviewer.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 3.5 LaTeX Agent Implementation
- [ ] 3.5.1 [Pending] [Developer] - Implement `src/agents/latex_agent.py` for document structuring, mandating programmatic SDK loading of skills | DoD: Agent dynamically rediscovers, activates, and injects its assigned skill via `pathlib.Path`.
- [ ] 3.5.2 [Pending] [QA] - Verify line length limits for `latex_agent.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 3.5.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `latex_agent.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.
- [ ] 3.6.4 [Pending] [QA] - Execute Hard Human-in-the-Loop Pipeline Pause and Inspection Tracking | DoD: Textual prose, factual citations, and TikZ layout structure manually vetted and formal execution of **Gate 3** sign-off.

## Phase 4: Content Generation & Orchestration
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The SDK Core orchestrator is implemented and verified. The pipeline generates a 25-30 page Hebrew Markdown draft with strict structural placeholders. A mandatory Human-in-the-Loop (HIL) pause for Positive AI Economy compliance is executed and approved. Bibliography is generated and strictly synchronized with RAG metadata.

### 4.1 SDK Core Orchestration
- [ ] 4.1.1 [Pending] [Developer] - Implement `src/sdk/core.py` to coordinate the CrewAI team and task execution flow | DoD: Core orchestrator script is fully functional.
- [ ] 4.1.2 [Pending] [QA] - Verify line length limits for `core.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 4.1.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `core.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 4.2 Pipeline Execution & Structural Requirements
- [ ] 4.2.1 [Pending] [Developer] - Update `logs/prompt_log.md` with the finalized system prompts | DoD: Log reflects the latest iteration of injected prompts.
- [ ] 4.2.2 [Pending] [Developer] - Execute the pipeline, mandating that `data/processed/output.md` strictly generates 25-30 pages of academic Hebrew content | DoD: Output draft is confirmed to meet the target page length volume.
- [ ] 4.2.3 [Pending] [Developer] - Explicitly inject and verify strict structural placeholders in Markdown for an automatic TOC, chapters, and headers/footers | DoD: Placeholders exist natively within the raw Markdown file.
- [ ] 4.2.4 [Pending] [Developer] - Explicitly inject and verify strict structural placeholders in Markdown for at least 1 image, 1 data graph, and 1 data summary table | DoD: Specific asset tags exist within the Markdown.
- [ ] 4.2.5 [Pending] [Developer] - Explicitly inject and verify strict structural placeholders in Markdown for 1 complex TikZ block diagram and the mathematical Drake Equation | DoD: TeX/TikZ placeholders properly embedded in Markdown.

### 4.3 Positive AI Economy & Human-in-the-Loop Gate
- [ ] 4.3.1 [Pending] [QA] - Enforce a hard system pause upon draft generation to mandate "Positive AI Economy" compliance | DoD: System execution halts pending manual review gate.
- [ ] 4.3.2 [Pending] [QA] - Human Operator Task: Manually inspect, edit, and formally approve textual prose and academic tone | DoD: Manual sign-off acquired for prose quality.
- [ ] 4.3.3 [Pending] [QA] - Human Operator Task: Manually inspect, edit, and formally approve validity of generated TikZ source formulas and math | DoD: Manual sign-off acquired for formulaic correctness.
- [ ] 4.3.4 [Pending] [QA] - Human Operator Task: Manually inspect, edit, and formally approve accuracy of factual references and citations | DoD: Manual sign-off acquired for factual alignment.

### 4.4 Bibliography Synchronization
- [ ] 4.4.1 [Pending] [Developer] - Generate the `.bib` bibliography file and map all sources accordingly | DoD: `.bib` file successfully compiled from extracted nodes.
- [ ] 4.4.2 [Pending] [QA] - Verify that all citations are perfectly synchronized with RAG metadata (page numbers, filenames, section headers) | DoD: Metadata strictly aligns with source PDFs, ensuring zero broken citations.
- [ ] 4.4.3 [Pending] [QA] - Execute Pre-Compilation Code and Schema Quality Sanity Evaluation | DoD: Verification that raw generated `.tex` script structure contains no breaking math syntax and formal execution of **Gate 4** sign-off.

## Phase 5: LaTeX Production & Security Sandbox
**Priority:** Medium | **Status:** Pending
**Definition of Done (DoD):** Advanced LaTeX tools are implemented. AI-generated Python scripts are strictly executed within a WSL Sandbox. A professional PDF is produced via a 4-pass build featuring a formal Cover Page, TikZ diagrams, and the Drake Equation.

### 5.1 Sandbox Security Protocol (WSL)
- [ ] 5.1.1 [Pending] [Architect] - Configure and enforce an isolated Windows Subsystem for Linux (WSL) Sandbox environment | DoD: Sandbox boundaries established and verified.
- [ ] 5.1.2 [Pending] [QA] - Ensure all AI-generated Python scripts (e.g., data graphs) are executed strictly within the WSL Sandbox | DoD: Execution occurs exclusively within isolated WSL session.

### 5.2 LaTeX Converter Implementation
- [ ] 5.2.1 [Pending] [Developer] - Implement `src/sdk/latex_converter.py` to transform Markdown syntax into valid TeX code | DoD: Converter successfully transpiles `.md` to `.tex`.
- [ ] 5.2.2 [Pending] [QA] - Verify line length limits for `latex_converter.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 5.2.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `latex_converter.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.

### 5.3 LaTeX Style Module & Cover Page
- [ ] 5.3.1 [Pending] [Developer] - Implement `src/sdk/latex_style.py` to manage headers, footers, and preamble configurations | DoD: Style module generates valid preamble formatting.
- [ ] 5.3.2 [Pending] [QA] - Verify line length limits for `latex_style.py` to trigger refactoring if > 150 lines | DoD: Line count explicitly checked and verified under 150 lines.
- [ ] 5.3.3 [Pending] [QA] - Run Ruff formatting checks and execute `pytest-cov` against `latex_style.py` | DoD: Zero Ruff violations detected and test coverage metrics reach >= 85%.
- [ ] 5.3.4 [Pending] [Developer] - Implement the formal Cover Page in the `.tex` source, strictly including: Subject, Authors, Date, Course, Lecturer | DoD: TeX document outputs formal, populated cover page.

### 5.4 Final Compilation Execution
- [ ] 5.4.1 [Pending] [QA] - Execute Pass 1: Run LuaLaTeX to generate initial auxiliary files | DoD: `.aux` and `.bcf` files generated without fatal halting.
- [ ] 5.4.2 [Pending] [QA] - Execute Pass 2: Run Biber/BibTeX to process the bibliography | DoD: Bibliography processes without unresolved citation errors.
- [ ] 5.4.3 [Pending] [QA] - Execute Pass 3: Run LuaLaTeX to weave citations and TOC | DoD: TOC populated and internal refs mapped.
- [ ] 5.4.4 [Pending] [QA] - Execute Pass 4: Run LuaLaTeX to finalize page numbers and cross-references | DoD: Final pass completes clean sync of all layout blocks.

### 5.5 Granular PDF Quality Assurance (QA)
- [ ] 5.5.1 [Pending] [QA] - Verify that the final PDF length is strictly between 25 and 30 pages | DoD: Final compiled artifact confirms page constraint.
- [ ] 5.5.2 [Pending] [QA] - Verify perfect BiDi support: Ensure RTL Hebrew text flows correctly and mixes seamlessly with LTR English terms | DoD: Visual validation confirms correct textual directionality.
- [ ] 5.5.3 [Pending] [QA] - Visually confirm the presence of at least one integrated Image | DoD: Visual confirmation complete.
- [ ] 5.5.4 [Pending] [QA] - Visually confirm the presence of at least one Python-generated Data Graph | DoD: Visual confirmation complete.
- [ ] 5.5.5 [Pending] [QA] - Visually confirm the presence of at least one Data Table without page overflow | DoD: Visual confirmation complete.
- [ ] 5.5.6 [Pending] [QA] - Visually confirm the presence of a complex TikZ Block Diagram | DoD: Visual confirmation complete.
- [ ] 5.5.7 [Pending] [QA] - Visually confirm the Drake Equation is rendered as a complex mathematical LaTeX "fancy formula" and not as plain text | DoD: Visual confirmation complete.

### 5.6 Comprehensive Project Documentation (README)
- [ ] 5.6.1 [Pending] [Architect] - Write the `README.md` "Project Overview" and "Architecture" sections | DoD: README sections populated.
- [ ] 5.6.2 [Pending] [Architect] - Write the `README.md` "Installation Instructions" section, explicitly detailing environment setup using `uv` | DoD: README instructions accurately reflect `uv` environment.
- [ ] 5.6.3 [Pending] [Architect] - Write the `README.md` "Usage Instructions" section, demonstrating how to trigger the autonomous AI pipeline | DoD: Usage CLI/SDK commands are documented.
- [ ] 5.6.4 [Pending] [Architect] - Write the `README.md` "Configuration Guide" detailing how to adjust `rate_limits.json` and agent skills | DoD: Config tweaks are documented.

### 5.7 Final Delivery
- [ ] 5.7.1 [Pending] [QA] - Finalize, version-tag, and securely archive `final_paper.pdf` | DoD: PDF hashed/archived as final output.
- [ ] 5.6.5 [Pending] [QA] - Final Multi-Pass LuaLaTeX Compilation Layout Audit | DoD: Output validation checks verify document length is strictly 25-30 pages with perfect BiDi alignment and formal execution of **Gate 5** artifact lock.

## Phase 6: Post-Generation Analysis & Token Economy
**Priority:** Medium | **Status:** Pending
**Definition of Done (DoD):** A comprehensive post-generation analysis is conducted within a dedicated Jupyter Notebook, focusing on parameter sensitivity and retrieval precision. A formal Token Economy Report is generated at `docs/token_economy_report.md`, detailing granular input/output token usage, financial expenditure based on pricing matrices, and budget projections. Strategic cost-optimization mechanisms are analyzed and documented.

### 6.1 Research, Analysis & Visualization (Jupyter Framework)
- [ ] 6.1.1 [Pending] [Architect] - Create the dedicated Jupyter Notebook `notebooks/analysis_results.ipynb` | DoD: Notebook file exists on disk.
- [ ] 6.1.2 [Pending] [Developer] - Implement the "Parameter Sensitivity Analysis" module within the notebook | DoD: Notebook contains operational code blocks for analysis.
- [ ] 6.1.3 [Pending] [QA] - Execute experiments to plot and analyze how varying RAG chunk sizes impact retrieval precision | DoD: Visual plots rendered in notebook.
- [ ] 6.1.4 [Pending] [QA] - Execute experiments to plot and analyze how varying RAG overlap sizes impact retrieval precision | DoD: Visual plots rendered in notebook.
- [ ] 6.1.5 [Pending] [QA] - Execute experiments to analyze how varying LLM temperature parameters impact agent hallucination rates | DoD: Analytical outcomes logged in notebook.
- [ ] 6.1.6 [Pending] [QA] - Execute experiments to analyze how varying LLM temperature parameters impact prose creativity and academic tone | DoD: Analytical outcomes logged in notebook.
- [ ] 6.1.7 [Pending] [Developer] - Document the findings of all sensitivity analysis experiments with specific data visualizations | DoD: Findings synthesized and published.

### 6.2 Token Economy & Comprehensive Cost Analysis
- [ ] 6.2.1 [Pending] [Architect] - Initialize the formal report file at `docs/token_economy_report.md` | DoD: Markdown file exists.
- [ ] 6.2.2 [Pending] [Developer] - Implement logic to calculate total Input Tokens used by every agent across all model interactions | DoD: Input tokens successfully tallied.
- [ ] 6.2.3 [Pending] [Developer] - Implement logic to calculate total Output Tokens used by every agent across all model interactions | DoD: Output tokens successfully tallied.
- [ ] 6.2.4 [Pending] [Developer] - Convert total token usage into actual financial metrics based on specific cost-per-million-tokens pricing matrices | DoD: Total financial cost calculated and verified.
- [ ] 6.2.5 [Pending] [Architect] - Document the real-time budget tracking efficiency throughout the project lifecycle | DoD: Tracking logs published to report.
- [ ] 6.2.6 [Pending] [QA] - Perform a comparative analysis between actual budget consumption and predicted budget estimates | DoD: Analysis written in the report.
- [ ] 6.2.7 [Pending] [Architect] - Develop and document a clear budget projection model for expanding the document size beyond 30 pages | DoD: Extrapolation model mapped in the report.

### 6.3 Cost Optimization Strategies
- [ ] 6.3.1 [Pending] [Architect] - Establish the "Optimization Reporting" section within `token_economy_report.md` | DoD: Markdown headers established.
- [ ] 6.3.2 [Pending] [QA] - Analyze and document the effectiveness of prompt compression techniques in reducing input costs | DoD: Analysis fully documented.
- [ ] 6.3.3 [Pending] [QA] - Analyze and document the impact of dynamic model routing, using smaller models for routing and reviewing tasks | DoD: Analysis fully documented.
- [ ] 6.3.4 [Pending] [QA] - Analyze and document the results of RAG filtering optimizations to minimize context window bloat | DoD: Analysis fully documented.
- [ ] 6.3.5 [Pending] [Architect] - Synthesize all optimization findings into actionable recommendations for future pipeline iterations | DoD: Recommendations formally listed.
- [ ] 6.3.6 [Pending] [QA] - Post-Production Token Optimization and Sensitivity Audit Sign-off | DoD: Financial cost report and parameter notebooks verified to compile completely and formal execution of **Gate 6** programmatic lock.
