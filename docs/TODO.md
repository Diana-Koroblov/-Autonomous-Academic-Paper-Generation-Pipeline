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
- [ ] 1.1.1 Initialize the workspace structure: `src/`, `tests/`, `config/`, `skills/`, `data/`, `logs/`, `assets/`, and `notebooks/`.
- [ ] 1.1.2 Configure `pyproject.toml` with strict Ruff rules and define `uv` dependencies.
- [ ] 1.1.3 Execute `uv` to explicitly generate the `uv.lock` file as the single source of truth for dependencies.
- [ ] 1.1.4 Initialize the TDD testing infrastructure: create the `tests/unit/` and `tests/integration/` directories.
- [ ] 1.1.5 Create a shared `tests/conftest.py` file to manage global test fixtures.
- [ ] 1.1.6 Create a secure `.gitignore` file to exclude sensitive local data and caches.
- [ ] 1.1.7 Create `.env-example` with dummy values for required API keys.
- [ ] 1.1.8 Create `config/rate_limits.json` to externalize all API and system thresholds.
- [ ] 1.1.9 Create `config/setup.json` to manage the main application configuration.

### 1.2 Shared Version Module
- [ ] 1.2.1 Create `src/shared/version.py` and explicitly initialize the version to `1.00`.
- [ ] 1.2.2 Verify that `version.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 1.2.3 Execute Ruff check on `version.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 1.3 SDK Gatekeeper Implementation
- [ ] 1.3.1 Create `src/sdk/gatekeeper.py` to handle API rate limiting, exponential backoff retries, and a strict FIFO Queue mechanism to manage overflow and backpressure.
- [ ] 1.3.2 Verify that `gatekeeper.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 1.3.3 Execute Ruff check on `gatekeeper.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 1.4 SDK Harness Implementation
- [ ] 1.4.1 Create `src/sdk/harness.py` to wrap agents for logging, context injection, and token tracking.
- [ ] 1.4.2 Verify that `harness.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 1.4.3 Execute Ruff check on `harness.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

## Phase 2: RAG Engine & Specialized Documentation
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The RAG engine architecture is documented and implemented. Core retrieval, parsing, and querying modules are separated into distinct files, each verified under the 150-line limit and passing the full QA protocol.

### 2.1 RAG Architectural Documentation
- [ ] 2.1.1 Write docs/PRD_rag_engine.md explicitly detailing the text-embedding-3-small model and the exact chunking parameters (1000 tokens size, 100 tokens overlap).
- [ ] 2.1.2 Place all source PDF documents regarding Extraterrestrials and Conspiracy Theories into the `data/` directory prior to engine ingestion.

### 2.2 RAG Core Module
- [ ] 2.2.1 Create `src/tools/rag_core.py` to manage base vector database connectivity.
- [ ] 2.2.2 Verify that `rag_core.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 2.2.3 Execute Ruff check on `rag_core.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 2.3 RAG Parser Module
- [ ] 2.3.1 Create src/tools/rag_parser.py for PDF extraction, strictly implementing the 1000/100 chunking logic and extracting metadata required for BibTeX (page numbers, file names, section headers).
- [ ] 2.3.2 Verify that `rag_parser.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 2.3.3 Execute Ruff check on `rag_parser.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 2.4 RAG Query Module
- [ ] 2.4.1 Create src/tools/rag_query.py, explicitly implementing Cosine Similarity for semantic retrieval and chunk ranking.
- [ ] 2.4.2 Verify that `rag_query.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 2.4.3 Execute Ruff check on `rag_query.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

## Phase 3: CrewAI Agent Intelligence & Skills Architecture
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The CrewAI team is deployed using the Skills pattern. Each agent (Researcher, Writer, Reviewer, LaTeX) is defined in a separate file, verified under the 150-line limit, and passing the full QA protocol. Explicit `SKILL.md` files guide agent behavior.

### 3.1 CrewAI Skills Repository
- [ ] 3.1.1 Create the `skills/` directory at the project root.
- [ ] 3.1.2 Write `skills/research_skill.md`, explicitly defining that it must govern fact-cross-referencing and prevent memory poisoning.
- [ ] 3.1.3 Write `skills/writing_skill.md`, explicitly defining that it must enforce academic Hebrew prose style, structural coherence, and a 25-30 page velocity target.
- [ ] 3.1.4 Write `skills/review_skill.md`, explicitly defining that it must mandate a strict truth-verification protocol against RAG chunks to eliminate hallucinations.
- [ ] 3.1.5 Write `skills/latex_skill.md`, explicitly defining that it must govern accurate TikZ syntax compilation, mathematical notation layout, and BiDi engine packages.

### 3.2 Researcher Agent Implementation
- [ ] 3.2.1 Create `src/agents/researcher.py` specializing in RAG-driven factual extraction. Explicitly mandate programmatic loading (SDK approach) of skills using CrewAI's `discover_skills` and `activate_skill` functions via `pathlib.Path`, ensuring the class dynamically rediscovers, activates, and injects its assigned skill.
- [ ] 3.2.2 Verify that `researcher.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 3.2.3 Execute Ruff check on `researcher.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 3.3 Writer Agent Implementation
- [ ] 3.3.1 Create `src/agents/writer.py` for drafting academic Hebrew content and managing placeholders. Explicitly mandate programmatic loading (SDK approach) of skills using CrewAI's `discover_skills` and `activate_skill` functions via `pathlib.Path`, ensuring the class dynamically rediscovers, activates, and injects its assigned skill.
- [ ] 3.3.2 Verify that `writer.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 3.3.3 Execute Ruff check on `writer.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 3.4 Reviewer Agent Implementation
- [ ] 3.4.1 Create `src/agents/reviewer.py` to perform fact-checking and tone verification. Explicitly mandate programmatic loading (SDK approach) of skills using CrewAI's `discover_skills` and `activate_skill` functions via `pathlib.Path`, ensuring the class dynamically rediscovers, activates, and injects its assigned skill.
- [ ] 3.4.2 Verify that `reviewer.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 3.4.3 Execute Ruff check on `reviewer.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 3.5 LaTeX Agent Implementation
- [ ] 3.5.1 Create `src/agents/latex_agent.py` for document structuring and technical element integration. Explicitly mandate programmatic loading (SDK approach) of skills using CrewAI's `discover_skills` and `activate_skill` functions via `pathlib.Path`, ensuring the class dynamically rediscovers, activates, and injects its assigned skill.
- [ ] 3.5.2 Verify that `latex_agent.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 3.5.3 Execute Ruff check on `latex_agent.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

## Phase 4: Content Generation & Orchestration
**Priority:** High | **Status:** Pending
**Definition of Done (DoD):** The SDK Core orchestrator is implemented and verified. The pipeline generates a 25-30 page Hebrew Markdown draft with strict structural placeholders. A mandatory Human-in-the-Loop (HIL) pause for Positive AI Economy compliance is executed and approved. Bibliography is generated and strictly synchronized with RAG metadata.

### 4.1 SDK Core Orchestration
- [ ] 4.1.1 Create `src/sdk/core.py` to coordinate the CrewAI team and task execution flow.
- [ ] 4.1.2 Verify that `core.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 4.1.3 Execute Ruff check on `core.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 4.2 Pipeline Execution & Structural Requirements
- [ ] 4.2.1 Update `logs/prompt_log.md` with the finalized system prompts.
- [ ] 4.2.2 Execute the pipeline, mandating that the output `data/processed/output.md` strictly generates 25-30 pages of academic Hebrew content.
- [ ] 4.2.3 Explicitly inject and verify strict structural placeholders in the Markdown for an automatic Table of Contents (TOC), ordered chapters, and academic headers/footers.
- [ ] 4.2.4 Explicitly inject and verify strict structural placeholders in the Markdown for at least 1 image, 1 data graph, and 1 data summary table.
- [ ] 4.2.5 Explicitly inject and verify strict structural placeholders in the Markdown for 1 complex TikZ block diagram and the mathematical Drake Equation.

### 4.3 Positive AI Economy & Human-in-the-Loop Gate
- [ ] 4.3.1 Enforce a hard system pause upon draft generation to mandate "Positive AI Economy" compliance.
- [ ] 4.3.2 Human Operator Task: Manually inspect, edit, and formally approve the textual prose and academic tone of the generated draft.
- [ ] 4.3.3 Human Operator Task: Manually inspect, edit, and formally approve the validity of the generated TikZ source formulas and mathematical equations.
- [ ] 4.3.4 Human Operator Task: Manually inspect, edit, and formally approve the accuracy of the factual references and citations.

### 4.4 Bibliography Synchronization
- [ ] 4.4.1 Generate the `.bib` bibliography file and map all sources accordingly.
- [ ] 4.4.2 Verify that all citations extracted by the Researcher Agent are perfectly synchronized with the RAG metadata (page numbers, filenames, and section headers) inside the `.bib` file to ensure absolute reference integrity.

## Phase 5: LaTeX Production & Security Sandbox
**Priority:** Medium | **Status:** Pending
**Definition of Done (DoD):** Advanced LaTeX tools are implemented. AI-generated Python scripts are strictly executed within a WSL Sandbox. A professional PDF is produced via a 4-pass build featuring a formal Cover Page, TikZ diagrams, and the Drake Equation.

### 5.1 Sandbox Security Protocol (WSL)
- [ ] 5.1.1 Configure and enforce an isolated Windows Subsystem for Linux (WSL) Sandbox environment.
- [ ] 5.1.2 Ensure all AI-generated Python scripts (e.g., for data graphs) are executed strictly within the WSL Sandbox to protect the host machine.

### 5.2 LaTeX Converter Implementation
- [ ] 5.2.1 Create `src/sdk/latex_converter.py` to transform Markdown syntax into valid TeX code.
- [ ] 5.2.2 Verify that `latex_converter.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 5.2.3 Execute Ruff check on `latex_converter.py` (0 violations) and run `pytest-cov` for >= 85% coverage.

### 5.3 LaTeX Style Module & Cover Page
- [ ] 5.3.1 Create `src/sdk/latex_style.py` to manage headers, footers, and preamble configurations.
- [ ] 5.3.2 Verify that `latex_style.py` strictly does not exceed 150 lines. If it does, refactor and split the logic.
- [ ] 5.3.3 Execute Ruff check on `latex_style.py` (0 violations) and run `pytest-cov` for >= 85% coverage.
- [ ] 5.3.4 Implement the formal Cover Page in the `.tex` source, strictly including: Subject, Authors (AI Agents), Date, Course Name, and Lecturer Name.

### 5.4 Final Compilation Execution
- [ ] 5.4.1 Execute Pass 1: Run LuaLaTeX to generate initial auxiliary files.
- [ ] 5.4.2 Execute Pass 2: Run Biber/BibTeX to process the bibliography.
- [ ] 5.4.3 Execute Pass 3: Run LuaLaTeX to weave citations and TOC.
- [ ] 5.4.4 Execute Pass 4: Run LuaLaTeX to finalize page numbers and cross-references.

### 5.5 Granular PDF Quality Assurance (QA)
- [ ] 5.5.1 Verify that the final PDF length is strictly between 25 and 30 pages.
- [ ] 5.5.2 Verify perfect BiDi support: Ensure right-to-left (RTL) Hebrew text flows correctly and mixes seamlessly with LTR English terms.
- [ ] 5.5.3 Visually confirm the presence of at least one integrated Image.
- [ ] 5.5.4 Visually confirm the presence of at least one Python-generated Data Graph.
- [ ] 5.5.5 Visually confirm the presence of at least one Data Table without page overflow.
- [ ] 5.5.6 Visually confirm the presence of a complex TikZ Block Diagram.
- [ ] 5.5.7 Visually confirm the Drake Equation is rendered as a complex mathematical LaTeX "fancy formula" and not as plain text.

### 5.6 Comprehensive Project Documentation (README)
- [ ] 5.6.1 Write the `README.md` "Project Overview" and "Architecture" sections.
- [ ] 5.6.2 Write the `README.md` "Installation Instructions" section, explicitly detailing environment setup using `uv`.
- [ ] 5.6.3 Write the `README.md` "Usage Instructions" section, demonstrating how to trigger the autonomous AI pipeline.
- [ ] 5.6.4 Write the `README.md` "Configuration Guide" detailing how to adjust `rate_limits.json` and agent skills.

### 5.7 Final Delivery
- [ ] 5.7.1 Finalize, version-tag, and securely archive `final_paper.pdf`.

## Phase 6: Post-Generation Analysis & Token Economy
**Priority:** Medium | **Status:** Pending
**Definition of Done (DoD):** A comprehensive post-generation analysis is conducted within a dedicated Jupyter Notebook, focusing on parameter sensitivity and retrieval precision. A formal Token Economy Report is generated at `docs/token_economy_report.md`, detailing granular input/output token usage, financial expenditure based on pricing matrices, and budget projections. Strategic cost-optimization mechanisms are analyzed and documented.

### 6.1 Research, Analysis & Visualization (Jupyter Framework)
- [ ] 6.1.1 Create the dedicated Jupyter Notebook `notebooks/analysis_results.ipynb`.
- [ ] 6.1.2 Implement the "Parameter Sensitivity Analysis" module within the notebook.
- [ ] 6.1.3 Execute experiments to plot and analyze how varying RAG chunk sizes impact retrieval precision.
- [ ] 6.1.4 Execute experiments to plot and analyze how varying RAG overlap sizes impact retrieval precision.
- [ ] 6.1.5 Execute experiments to analyze how varying LLM temperature parameters impact agent hallucination rates.
- [ ] 6.1.6 Execute experiments to analyze how varying LLM temperature parameters impact prose creativity and academic tone.
- [ ] 6.1.7 Document the findings of all sensitivity analysis experiments with specific data visualizations.

### 6.2 Token Economy & Comprehensive Cost Analysis
- [ ] 6.2.1 Initialize the formal report file at `docs/token_economy_report.md`.
- [ ] 6.2.2 Implement logic to calculate total Input Tokens used by every agent across all model interactions.
- [ ] 6.2.3 Implement logic to calculate total Output Tokens used by every agent across all model interactions.
- [ ] 6.2.4 Convert total token usage into actual financial metrics based on the specific cost-per-million-tokens pricing matrices of used providers.
- [ ] 6.2.5 Document the real-time budget tracking efficiency throughout the project lifecycle.
- [ ] 6.2.6 Perform a comparative analysis between actual budget consumption and predicted budget estimates.
- [ ] 6.2.7 Develop and document a clear budget projection model for expanding the document size beyond the current 30-page limit.

### 6.3 Cost Optimization Strategies
- [ ] 6.3.1 Establish the "Optimization Reporting" section within the `token_economy_report.md`.
- [ ] 6.3.2 Analyze and document the effectiveness of prompt compression techniques in reducing input costs.
- [ ] 6.3.3 Analyze and document the impact of dynamic model routing, specifically using smaller models for routing and reviewing tasks.
- [ ] 6.3.4 Analyze and document the results of RAG filtering optimizations to minimize context window bloat.
- [ ] 6.3.5 Synthesize all optimization findings into actionable recommendations for future pipeline iterations.
