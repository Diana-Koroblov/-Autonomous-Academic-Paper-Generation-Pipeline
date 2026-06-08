# Product Requirements Document (PRD): Autonomous AI Pipeline for Academic Paper Generation

## 1. Project Overview & Context

### Goal
The goal of this project is to develop an AI-based autonomous pipeline using CrewAI and RAG (Retrieval-Augmented Generation) technology to research, write, and format an academic paper or book of 25-30 pages. The chosen subject is "Extraterrestrials and Conspiracy Theories" (e.g., SETI, Roswell).

### User Problem
Writing a comprehensive academic paper is time-consuming, requiring extensive research across multiple sources, synchronization between facts and citations, and adherence to strict formatting standards (LaTeX). This system aims to automate the process while maintaining factual accuracy and academic quality.

### Market Analysis & Target Audience
*   **Academia:** Students and researchers needing rapid information synthesis.
*   **UFO Researchers:** Independent bodies interested in professional documentation of data and evidence.
*   **Content Creators:** Scientific or pseudo-scientific content creators looking for a broad, reasoned knowledge base.

---

## 2. Measurable Goals, KPIs & Acceptance Criteria

### Key Performance Indicators (KPIs)
*   **RAG Retrieval Latency:** The system must achieve a maximum allowable time of < 1.5 seconds for individual chunk retrieval from the vector database.
*   **Orchestration Token Efficiency:** The system targets a high ratio of useful synthesized text relative to input tokens to ensure cost-effective generation.
*   **Compilation Success Rate:** 100% successful builds across multi-pass LuaLaTeX executions must be maintained during all testing and production cycles.
*   **Agent Response Timeout Boundaries:** Strict response limits are enforced for every agent before triggering the Gatekeeper retry and FIFO queuing mechanisms to prevent pipeline stagnation.

### Final Product Acceptance Criteria:
*   **Document Length:** 25-30 full pages.
*   **Cover Page:** Must include Subject, Authors (AI Agents), Date, Course Name, and Lecturer Name.
*   **Academic Structure:** Automatic Table of Contents, ordered chapters, headers, and footers.
*   **Bibliography:** Complete list of sources at the end of the document with linked citations.
*   **Visual Elements:**
    *   At least 1 Image.
    *   At least 1 data graph generated using Python (Matplotlib/Seaborn).
    *   At least 1 data summary table.
    *   1 complex block diagram using TikZ (within LaTeX).
*   **Scientific Content:** Inclusion of the Drake Equation in a complex mathematical format using LaTeX.

---

## 3. Functional & Non-Functional Requirements

### Functional Requirements:
1.  **Orchestration (CrewAI):** The system will operate a team of agents running natively on the **Google Gemini API Ecosystem**:
    *   **Researcher:** Gathers information from RAG and the web (Model: **`gemini-1.5-flash`**).
    *   **Writer:** Drafts chapters in an academic style (Model: **`gemini-1.5-flash`**).
    *   **Reviewer:** Performs fact-checking and quality control (Model: **`gemini-1.5-pro`**).
    *   **LaTeX Agent:** Formats content into a standard academic layout (Model: **`gemini-1.5-flash`**).
2.  **RAG Pipeline:** Retrieves factual data from pre-loaded PDF documents. Detailed technical specifications for the RAG engine are decoupled and fully mapped inside `docs/PRD_rag_engine.md`.
3.  **Workflow:**
    *   Phase A: Generate a full draft in Markdown format.
    *   Phase B: Convert Markdown to a `.tex` file via the dedicated agent.
    *   Phase C: Embed graphical elements and Python-generated code into the LaTeX source.

### Non-Functional Requirements:
*   **Reproducibility:** Use `uv.lock` to ensure a consistent and reproducible environment.
*   **Performance:** Support parallel chapter writing where possible.
*   **Language Support:** Full BiDi (Hebrew/English) support within the generated PDF.

### Security Requirements:
*   **Execution Sandboxing:** Hard requirement for running all dynamic, AI-generated Python plotting code strictly inside an isolated Windows Subsystem for Linux (WSL) Sandbox environment to protect the host architecture.
*   **API Key Protection & Secret Leak Prevention:** Strict zero-hardcoding mandates require all LLM and vector database credentials to be extracted into `.env` runtime containers, seeking **`GEMINI_API_KEY`** validated via an `.env-example` boilerplate.
*   **Data Poisoning Mitigations:** Mandatory prompt-level boundaries are enforced for the Researcher Agent to prevent untrusted context from overriding core system constraints (Prompt Injection and Memory Poisoning prevention).

### User Stories & Use Cases:
*   **As an academic researcher**, I want the AI to automatically gather factual data from my provided PDFs (RAG), so that I don't have to manually verify every base fact.
*   **As a content editor**, I want the system to output a preliminary Markdown draft before LaTeX compilation, so that I can easily review and adjust the text.
*   **As a reader**, I want all bibliographic citations to be accurately linked to the reference list, so that I can easily verify the sources.

---

## 4. Assumptions, Dependencies, Constraints & Out-of-Scope

### Project Assumptions:
*   **Source Quality:** It is assumed that pre-loaded PDF materials in the RAG repository are authoritative, factually sound, and have been pre-vetted for academic integrity.
*   **API Availability:** The system relies on uninterrupted, high-uptime access to the **Google Gemini API Ecosystem** within standard Tier limits.
*   **Resource Sufficiency:** The host machine is assumed to run a fully configured MiKTeX environment supporting LuaLaTeX compilation engines and necessary BiDi packages.

### Technical Constraints:
*   **Compilation Engine:** Must use **LuaLaTeX** (via MiKTeX) to ensure perfect BiDi support for mixed Hebrew and English text.
*   **Compilation Process:** Requires approximately 4 compiler runs (including BibTeX/biber) to ensure all citations, TOC, and internal references are synchronized.
*   **Dependencies:** The system relies on LLM access (Google Gemini API) via CrewAI.

### Out-of-Scope:
*   **Automatic submission to academic journals.**
*   **Generating video content from the paper.**
*   **Physical verification of evidence (reliance on RAG sources only).**

---

## 5. Timeline & Milestones

| Milestone | Description | Expected Deliverable | Mandatory Review Gate (Review Point) |
| :--- | :--- | :--- | :--- |
| **Phase 1: Project Setup** | Define environment (uv), folder structure, and LLM connection. | Functional workspace. | **Gate 1:** Validate `uv.lock` environment stability and zero-Ruff structural configuration sign-off. |
| **Phase 2: RAG & Agent Implementation** | Load PDFs, define retrieval tools, and build the Crew. | Agents successfully retrieving info. | **Gate 2:** Verify programmatic Skill loading mechanics and RAG connectivity response times ($<1.5$s). |
| **Phase 3: Content Generation (Markdown)** | Run the pipeline to create the full draft (25-30 pages). | Detailed `output.md` file. | **Gate 3:** Execute the **Human-in-the-Loop Pause**; formal approval of prose, academic tone, and reference mappings. |
| **Phase 4: LaTeX Formatting & Graphics** | Convert to TeX, implement TikZ, graphs, and Drake Equation. | `.tex` file ready for compilation. | **Gate 4:** Code-level inspection and compilation sanity check of raw TikZ source blocks and math layouts. |
| **Phase 5: Final Compilation & Review** | Run LuaLaTeX 4 times and perform final quality check. | Perfect `final_paper.pdf`. | **Gate 5:** Page-budget validation (strictly 25-30 pages), perfect BiDi alignment check, and artifact lock. |
| **Phase 6: Post-Prod Analysis & Token Economy** | Execute sensitivity experiments in Jupyter and generate final budget financial reports. | Document `docs/token_economy_report.md` and complete analysis notebook. | **Gate 6:** Financial audit compliance sign-off and cost-optimization strategy verification. |

---
**Prepared by:** Senior Product Manager & System Architect
**Date:** June 8, 2026
