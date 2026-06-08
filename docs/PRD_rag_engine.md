# Product Requirements Document (PRD): Specialized RAG Knowledge Engine Module

## 1. Module Overview & Technical Context
This standalone document defines the granular product and mathematical requirements for the modular Retrieval-Augmented Generation (RAG) subsystem. The purpose of this engine is to provide strict factual grounding, extract structural citations, and prevent context poisoning for the autonomous academic crew.

## 2. Granular Functional Architecture & Ingestion Mechanics
* **Text Extraction Protocol:** The ingestion pipeline must accurately parse local text and metadata from multi-source PDF layout files stored within the `data/raw/` registry.
* **Granular Chunking Strategy:** Ingested documents must be split into atomic text nodes using a strict sliding-window chunk size of **1000 tokens**, with a continuous overlapping boundary of **100 tokens** to ensure contextual prose preservation across chunk edges.
* **Vector Vectorization Pipeline:** All text segments must be mathematically processed using the native `text-embedding-3-small` OpenAI foundational model.
* **Metadata Schema Enforcement:** Every generated vector node must strictly append and map the following structural attributes for BibTeX source compilation:
  * `source_filename`: Exact origin file name string.
  * `page_number`: Integer tracking the exact physical layout page.
  * `section_header`: Closest ancestral markdown or document section hierarchy string.

## 3. Mathematical Retrieval & Query Optimization Criteria
* **Semantic Search Metric:** Computational query lookups against the local vector collection must compute the directional proximity of nodes utilizing the **Cosine Similarity** vector space formula:
  $$sim(q, d) = \frac{q \cdot d}{\|q\| \|d\|} = \cos(\theta)$$
* **Context Budget Gate:** The engine must rank lookups and return strictly the top $K$ highest-scoring chunks ($K$ dynamically driven by `config/setup.json`), ensuring the input context length window does not cause downstream LLM saturation.
* **Anti-Hallucination Isolation Boundary:** The search routing must act as a hard fence. If zero chunks meet a threshold score of $\ge 0.72$ similarity, the query logic must return an empty buffer instead of generating loose synthetic context.

## 4. Operational Performance Targets (KPIs)
* **Average Query Latency:** Under a standard production index, individual lookup lookups must return sorted nodes in $\le 1.5$ seconds.
* **Metadata Completeness Rate:** 100% of retrieved contexts passed to the Researcher Agent must maintain intact metadata tables to ensure zero anonymous citations.

---
**Prepared by:** Senior Product Manager & Core Systems Architect  
**Date:** June 8, 2026
