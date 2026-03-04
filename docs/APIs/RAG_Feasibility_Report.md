# RAG Feasibility Report

**Deliverable:** P3-2.2 — Report on API readiness for RAG
**Date:** March 2026
**Script:** `scripts/rag_feasibility_test.py`

---

## Executive Summary

This report documents the results of the Turath RAG feasibility test, which evaluated whether the platform's REST APIs can supply clean, structured data to a hypothetical external Retrieval-Augmented Generation (RAG) pipeline.

The test maps directly to the six RAG use cases outlined in the NEH DHAG grant:

| # | Grant Use Case | API Support | Result |
|---|---------------|-------------|--------|
| 1 | Question answering from curated content | IIIF in-document search locates exact pages | ✅ |
| 2 | Text summarization | Full page text per-chunk via annotations endpoint | ✅ |
| 3 | Knowledge cutoff mitigation | Live API serves current, domain-specific content | ✅ |
| 4 | Citation-backed generation | Every word has pixel-level `x,y,w,h` bounding box | ✅ |
| 5 | Smart searching | HOCR fulltext search returns ranked, relevant records | ✅ |
| 6 | Context-aware document linking | Rich Dublin Core metadata enables cross-record context | ✅ |

**Conclusion: Highly Feasible.** All six grant-defined RAG use cases are supported by the current API architecture.

---

## Background: RAG and the NEH Grant Vision

The NEH DHAG grant outlined a strategic AI vision centred on coupling **Knowledge Graphs** and **Large Language Models (LLMs)** via Retrieval-Augmented Generation. The goal is to leverage Turath's curated content to mitigate known LLM shortcomings:

- **Knowledge cutoff** — LLMs are trained to a fixed date; Turath's live API provides current, curated content
- **Hallucinations** — RAG grounds responses in source documents rather than model memory
- **Lack of citations** — Turath's pixel-level bounding boxes allow exact visual citations on manuscript pages
- **Domain knowledge gaps** — LLMs lack Arabic historical knowledge; Turath fills this gap
- **Prompt sensitivity** — Structured metadata reduces dependence on fragile prompt wording
- **Ethical/bias concerns** — Responses are traceable to specific, citable source passages

This test confirms the infrastructure is ready for this vision.

---

## Testing Methodology

The test script (`scripts/rag_feasibility_test.py`) simulates an external RAG service querying the Turath APIs across five sequential steps:

1. **HOCR full-text search** — find relevant records by content, not just metadata
2. **Rich metadata extraction** — extract all 12 Dublin Core / QDC custom fields
3. **Multi-page OCR iteration** — walk through all pages until no HOCR data found
4. **IIIF in-document search** — use the Content Search API to locate specific passages
5. **LLM context block generation** — assemble structured prompt blocks per page

---

## Test Results (Local Environment)

### Step 1: HOCR Full-Text Search (Use Case 5 — Smart Searching)

```
Query: custom_fields.turath\:fulltext:نجد
Result: 14 records found
```

The HOCR search API returns ranked, relevant records based on OCR content — not just metadata. A RAG pipeline can use this to pre-filter the corpus to the most relevant books before fetching page text.

---

### Step 2: Rich Metadata Extraction (Use Case 6 — Document Linking)

All 12 Dublin Core / QDC fields extracted per record:

```
Title          : 001_تاريخ_نجد
Creator        : (from turath:creator_arabic)
Publisher      : Riyadh: Dār al-thulūthiyya lil-nashr wa-l-tawzīʿ
Date           : 2010
Language       : Arabic
Resource Type  : Book
Coverage       : 1157 – 1212 (Hijri years)
Source         : archive.org
Rights         : Creative Commons Attribution 4.0 International
Record ID(PID) : 5nja4-5r064
```

This structured metadata allows a RAG pipeline to:
- Filter documents by language, time period, or geographic coverage before retrieval
- Build Knowledge Graph nodes from creator/subject/coverage relationships
- Provide LLM responses with proper bibliographic attribution

---

### Step 3: Multi-Page OCR Iteration (Use Case 4 — Citation-Backed Generation)

```
Record: qbs2f-xsr21
Pages with OCR text: 47
Total words extracted: 11,677
Words with bounding-box citations: 11,677 (100%)
```

Every word is available as a separate page-level chunk with an exact pixel bounding box:

```
Sample word citations (page p001):
  • "المملكة"  @ pixel bbox 589,178,93,58
  • "العربية"  @ pixel bbox 496,178,93,58
  • "السعودية" @ pixel bbox 403,178,93,58
```

These coordinates allow a future LLM interface to draw a highlight box directly on the scanned manuscript image when citing a passage — directly addressing the grant's "lack of sources, citations, evidence of explainability" concern.

---

### Step 4: IIIF In-Document Search (Use Case 1 — Question Answering)

```
Query: نجد (within record 5nja4-5r064)
IIIF search hits: 117 across pages p007, p011–p017, ...
```

The IIIF Content Search API locates the exact pages where a query term appears within a specific book. A RAG pipeline can use this to:
1. Search across records with the fulltext API (Step 1)
2. Then drill into specific pages using IIIF search
3. Retrieve only the relevant page chunks — reducing LLM context window usage

---

### Step 5: LLM Context Block (Use Cases 1, 2, 3)

The combined metadata + page text produces a structured prompt block:

```
=================================================================
DOCUMENT CONTEXT FOR LLM / RAG PIPELINE
=================================================================

BIBLIOGRAPHIC METADATA (Dublin Core / QDC):
--------------------------------------------
Title          : تاريخ ابن عباد
Publisher      : الأمانة العامة للاحتفال، المملكة العربية السعودية
Date           : 1999
Language       : Arabic
Resource Type  : Book
Coverage       : 1900-01-01 – 1950-12-31
Rights         : Creative Commons Attribution 4.0 International
Record ID (PID): qbs2f-xsr21

CONTENT — P001:
-----------------------------------------
المملكة العربية السعودية الأمانة العامة للاحتفال بمرور مائة عام على
تأسيس المملكة ... تاريخ ابن عباد ... تأليف محمد بن حمد بن عباد العوسجي
دراسة وتحقيق الأستاذ الدكتور عبد الله بن يوسف الشبل...

SAMPLE WORD CITATIONS:
  • "المملكة"  @ pixel bbox 589,178,93,58
  • "العربية"  @ pixel bbox 496,178,93,58
=================================================================
```

This block is directly consumable by any LLM API (Claude, GPT-4, Gemini, etc.) without the consuming application needing to perform any PDF parsing or OCR.

---

## Architectural Benefits for RAG

### 1. Page-Level Chunking — Optimal for LLMs
The annotations endpoint (`/annotations/{pid}/{page}`) returns text per manuscript page. Pages of 100–400 words map naturally to typical LLM context chunk sizes, bypassing the need for complex semantic text-splitting algorithms.

### 2. Zero OCR Overhead
OCR processing is done once at ingestion time. The RAG pipeline receives clean text via lightweight JSON API calls — no PDF downloading, no Tesseract, no post-processing.

### 3. Pixel-Level Visual Citations
The `x,y,w,h` bounding boxes returned for every word enable future AI interfaces to render exact visual citations on the original manuscript image — directly addressing the NEH grant's explainability and ethical traceability goals.

### 4. Knowledge Graph Ready
The rich Dublin Core metadata (creator, subject, coverage, relation) provides the structured entity data needed to build a Knowledge Graph layer on top of the LLM retrieval — exactly as envisioned in the grant's "Knowledge Graphs AND LLMs" strategy.

### 5. Multilingual Support
The Arabic language analyzer in OpenSearch ensures that Arabic root forms retrieve all morphological variants, giving a RAG pipeline linguistically aware results without any consumer-side NLP.

---

## Next Steps for a Production RAG System

To fully operationalise this for a live RAG application, the following steps are needed on the consumer side:

1. **Corpus crawler** — iterate all records and pages (`p001`…`pNNN` until 404) to build the text corpus
2. **Embedding model** — vectorise each page chunk using a multilingual Arabic embedding model (e.g., `intfloat/multilingual-e5-large` or OpenAI `text-embedding-3-large`)
3. **Vector database** — store embeddings alongside metadata in a vector store (Postgres + pgvector, Milvis, or Pinecone)
4. **Knowledge Graph layer** — build entity nodes (people, places, dates) from `turath:creator_arabic`, `turath:coverage_spatial`, `turath:coverage_temporal_*` fields
5. **Retrieval pipeline** — combine semantic vector search with HOCR keyword search for hybrid retrieval
6. **LLM integration** — pass retrieved page chunks + metadata to Claude, GPT-4, or a locally hosted Arabic-capable model
