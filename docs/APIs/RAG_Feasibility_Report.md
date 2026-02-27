# RAG Feasibility Test Report

**Date:** October 26, 2025
**Subject:** API Readiness for Retrieval-Augmented Generation (RAG) Pipelines

## Executive Summary
This document summarizes the findings from the RAG Feasibility Test (`scripts/rag_feasibility_test.py`). The objective was to determine if the existing Turath InvenioRDM REST APIs can successfully provide clean, structured data (metadata and full-text OCR) to a hypothetical external LLM/RAG pipeline.

**Conclusion: Highly Feasible.** The current API architecture is well-suited for external RAG integration without requiring consumer-side PDF parsing.

## Testing Methodology
A Python script was developed to simulate an external service querying the InvenioRDM instance. The script performs two actions:
1. Queries the standard metadata search API (`GET /api/records?sort=newest`) to find published records.
2. Queries the custom IIIF Search Service Annotations API (`GET /annotations/{record_pid}/p001`) to retrieve the extracted HOCR text for a specific page.

The retrieved data is then formatted into a prompt context block suitable for an LLM.

## Results

### 1. Metadata Retrieval (Success)
The standard InvenioRDM API returns deeply structured JSON containing all necessary bibliographic data (Title, Authors, Publication Date, Resource Type, Description). This maps perfectly to RAG metadata filters or document headers.

### 2. Full-Text Retrieval (Success)
Instead of forcing a RAG pipeline to download heavy PDFs and run its own OCR, our system exposes the pre-processed text via the IIIF annotations endpoint (`https://invenio.turath-project.com:5001/annotations/{pid}/{page}`).

The script successfully extracted 248 characters of clean Arabic text from Page 1 of record `10zkp-d5z36` ("001_تاريخ_نجد").

### 3. Generated LLM Context Window
The combination of metadata and page-level text resulted in an excellent, highly structured prompt block:

```text
=================================================================
DOCUMENT CONTEXT FOR LLM (RAG)
=================================================================

METADATA:
---------
Title: 001_تاريخ_نجد
Authors: Unknown
Record ID (PID): 10zkp-d5z36
Publication Date: 2010
Resource Type: publication-book

DESCRIPTION:
------------
Part I and Part II, together titled Tārīkh Najd; 1107 pages. Edition: al-Ṭabʿah 1

CONTENT (PAGE 1):
-----------------
﻿٤ - فصول وأبحاث جغرافية وتاريخية عن جزيرة العرب ﻿نبذة تاريخية عن نجد ﻿أملاها الأمير ضاري بن فهيد الرشيد ( .... - ١٣٣١ ه ) وكتبها الأستاذ وديع البستاني ( ١٣٠٢ - ١٣٧٣ ه ) ﻿منشورات دار اليمامة للبحث والترجمة والنشر - الرياض - المملكة العربية السعودية
=================================================================
```

## Architectural Benefits for RAG
1. **Page-Level Chunking:** Because the IIIF API serves text per page (`/annotations/pid/p001`, `p002`, etc.), the RAG pipeline naturally gets document chunks that roughly align with an LLM's ideal context size, bypassing complex semantic chunking logic.
2. **Zero OCR Overhead:** The heavy lifting (Tesseract OCR generation) is done once during ingestion. The RAG pipeline only deals with lightweight JSON strings.
3. **Accurate Bounding Boxes:** If the LLM needs to cite the exact location on the page, the raw JSON response contains `x,y,w,h` coordinates for every single word.

## Next Steps for a Production RAG System
To fully operationalize this for a real RAG application, the following would be needed on the consumer side:
- A crawler script that iterates through all pages of a record (using the page count found in the manifest or simply incrementing `p00X` until a 404 is hit).
- An embedding model (like `text-embedding-ada-002` or a multilingual equivalent for Arabic) to vectorise the page text.
- A vector database (like Pinecone, Milvus, or Postgres+pgvector) to store the chunks alongside the metadata.
