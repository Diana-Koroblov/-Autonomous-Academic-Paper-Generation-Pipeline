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
1.  **Orchestration (CrewAI):** The system will operate a team of agents:
    *   **Researcher:** Gathers information from RAG and the web.
    *   **Writer:** Drafts chapters in an academic style.
    *   **Reviewer:** Performs fact-checking and quality control.
    *   **LaTeX Agent:** Formats content into a standard academic layout.
2.  **RAG Pipeline:** Retrieves factual data from pre-loaded PDF documents.
3.  **Workflow:**
    *   Phase A: Generate a full draft in Markdown format.
    *   Phase B: Convert Markdown to a `.tex` file via the dedicated agent.
    *   Phase C: Embed graphical elements and Python-generated code into the LaTeX source.

### Non-Functional Requirements:
*   **Reproducibility:** Use `uv.lock` to ensure a consistent and reproducible environment.
*   **Performance:** Support parallel chapter writing where possible.
*   **Language Support:** Full BiDi (Hebrew/English) support within the generated PDF.

### User Stories & Use Cases:
*   **As an academic researcher**, I want the AI to automatically gather factual data from my provided PDFs (RAG), so that I don't have to manually verify every base fact.
*   **As a content editor**, I want the system to output a preliminary Markdown draft before LaTeX compilation, so that I can easily review and adjust the text.
*   **As a reader**, I want all bibliographic citations to be accurately linked to the reference list, so that I can easily verify the sources.

---

## 4. Assumptions, Dependencies, Constraints & Out-of-Scope

### Technical Constraints:
*   **Compilation Engine:** Must use **LuaLaTeX** (via MiKTeX) to ensure perfect BiDi support for mixed Hebrew and English text.
*   **Compilation Process:** Requires approximately 4 compiler runs (including BibTeX/biber) to ensure all citations, TOC, and internal references are synchronized.
*   **Dependencies:** The system relies on LLM access (e.g., OpenAI or Anthropic) via CrewAI.

### Out-of-Scope:
*   Automatic submission to academic journals.
*   Generating video content from the paper.
*   Physical verification of evidence (reliance on RAG sources only).

---

## 5. Timeline & Milestones

| Milestone | Description | Expected Deliverable |
| :--- | :--- | :--- |
| **Phase 1: Project Setup** | Define environment (uv), folder structure, and LLM connection. | Functional workspace. |
| **Phase 2: RAG & Agent Implementation** | Load PDFs, define retrieval tools, and build the Crew. | Agents successfully retrieving info. |
| **Phase 3: Content Generation (Markdown)** | Run the pipeline to create the full draft (25-30 pages). | Detailed `output.md` file. |
| **Phase 4: LaTeX Formatting & Graphics** | Convert to TeX, implement TikZ, graphs, and Drake Equation. | `.tex` file ready for compilation. |
| **Phase 5: Final Compilation & Review** | Run LuaLaTeX 4 times and perform final quality check. | Perfect `final_paper.pdf`. |

---
**Prepared by:** Senior Product Manager & System Architect
**Date:** June 8, 2026
