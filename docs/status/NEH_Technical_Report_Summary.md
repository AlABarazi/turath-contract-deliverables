# Turath Project: NEH Technical Report Summary

**Deliverable:** P3-3.4 — NEH Report Input
**Date:** March 2026
**Subject:** Technical Achievements and System Capabilities for NEH Grant Reporting
**Grant:** Digital Humanities Advancement Grant (DHAG) — Level I, Award No. HAA-287905-22
**Purpose:** Technical input for the NEH progress report, directly addressing the objectives and framework established in the project's White Paper.

---

## 1. Fulfilling the Infrastructure Vision: InvenioRDM Deployment

Following the technical evaluation exercise described in the White Paper, InvenioRDM was selected as Turath's primary data repository. In this phase, we successfully transitioned that vision into a fully operational, production-ready platform. The system is deployed on Amazon Web Services (AWS ECS Fargate) and is accessible at `https://invenio.turath-project.com`.

The platform fully implements the **FAIR data principles** (Findable, Accessible, Interoperable, Reusable) established as a core requirement in the White Paper:

- **Findable** — Every record is assigned a persistent identifier (PID/OAI) and indexed in OpenSearch with Arabic-language analysis for discoverability
- **Accessible** — Records and files are publicly accessible via documented REST APIs with no authentication required for published content
- **Interoperable** — The platform implements IIIF Presentation API 2.0, IIIF Content Search API 1.0, and OAI-PMH metadata harvesting, enabling integration with any IIIF-compliant viewer or harvesting system
- **Reusable** — All records carry structured Dublin Core / QDC metadata with explicit rights statements, temporal/geographic coverage, and provenance

---

## 2. The Three CoA Digital Outputs — Achieved

The White Paper identified three primary digital outputs for the Chronicles of Arabia initiative. This phase delivers all three:

### Output 1: Digital Reproduction (Scanned Images)

High-resolution scanned PDFs are stored in Amazon S3 and served via the **Cantaloupe IIIF Image Server** with FilesystemCache. The system generates pyramidal image tiles on demand with a cache pre-warming strategy, achieving cached page-load times below 0.5 seconds. Technical specifications follow FADGI and Harvard University Library digitisation standards.

### Output 2: Enriched Metadata

A comprehensive **Qualified Dublin Core (QDC)** metadata schema has been implemented as custom fields in InvenioRDM under the `turath:` namespace. The schema maps all 15 core Dublin Core elements — Title, Creator, Contributor, Publisher, Date, Language, Format, Subject, Description, Identifier, Relation, Source, Type, Coverage, and Rights — plus Turath-specific extensions (temporal/spatial coverage, Arabic-script creator names, bibliographic citation, script type, rights URI).

The deposit form exposes all fields through InvenioRDM's web UI, enabling curators to enter and refine metadata iteratively without technical assistance. The schema was developed in close alignment with the Turāth Metadata Guidelines (based on DCMI standards) and is fully compatible with OAI-PMH harvesting, supporting long-term interoperability goals.

### Output 3: Extracted and Structured Digital Text

The White Paper described the **Digital Text Pipeline** as the central technological challenge — extracting and structuring Arabic text from scanned chronicles using OCR. This phase completes that pipeline:

**OCR Pipeline (eScriptorium → HOCR):** Chronicle manuscripts were processed through eScriptorium (Kraken OCR engine), producing PageXML output. This PageXML was converted to HOCR format for integration into the InvenioRDM search and annotation architecture. HOCR retains the word-level bounding box coordinates from PageXML, preserving the spatial precision needed for visual citation and text overlay.

**Full-Text Indexing:** A custom `turath:fulltext` field in OpenSearch aggregates the text from all HOCR pages per record. The field uses a **custom Arabic text analyzer** with morphological stemming and stop-word removal, enabling search on root word forms. Users can query across the entire corpus text via the standard API (`custom_fields.turath\:fulltext:"phrase"`).

**In-Document Text Exploration:** A custom IIIF Content Search API microservice allows users to search within a specific chronicle in the Mirador viewer, with results highlighted at the exact word location on the page. This directly replaces and supersedes the TEI Publisher short-term solution described in the White Paper, providing native in-repository text exploration without requiring a separate application.

---

## 3. Key Technical Milestones

### A. Native Text Exploration: IIIF & Mirador 3

The platform now delivers fully integrated, native manuscript exploration:

- **Dynamic IIIF Manifests:** Multi-page PDFs are automatically mapped to individual IIIF canvases. Each manifest embeds the search service URL, enabling in-viewer search out of the box
- **Mirador 3 with Text Overlay:** A custom Mirador bundle incorporates the `textoverlay-mirador` plugin, rendering every OCR word as a selectable, hoverable HTML element positioned over the scanned page. Users can select and copy Arabic text directly from manuscript images
- **IIIF Content Search:** The search microservice processes queries in parallel across all HOCR pages and returns bounding-box annotations compatible with Mirador's search panel
- **High-Performance Tiling:** Cantaloupe with derivative caching reduces high-resolution tile delivery to under 0.5 seconds for cached pages

### B. Arabic Full-Text Search Infrastructure

- **Custom OpenSearch mapping** with Arabic language analyzer (stemming, stop-word removal, Unicode normalisation)
- **Search result highlighting:** snippets with `<em>` markup shown in the search results UI
- **Dual-mode search UI:** metadata search (title, creator, publisher) and full-text OCR search, accessible from homepage and search page
- **Faceted filtering:** by resource type, language, date range, and subject
- **IIIF Search microservice:** parallel processing across up to 175 pages per record; 99+ hits demonstrated for a single-record search

### C. Scalable Cloud Infrastructure

- **AWS ECS Fargate:** five containerised services — Web UI, Web API, Celery workers, IIIF Search microservice, and Cantaloupe — independently scalable
- **Infrastructure as Code (Terraform):** entire platform codified for reproducible deployments, supporting the planned migration to Harvard institutional infrastructure
- **Automated CI/CD:** GitHub Actions pipeline builds and registers three Docker images on every code push
- **Data durability:** Amazon RDS with 7-day point-in-time recovery (RPO < 5 minutes); S3 with versioning; documented disaster recovery runbook

### D. Long-Term Preservation Alignment

The platform's architecture aligns with the White Paper's commitment to long-term preservation goals:

- **PREMIS-compatible metadata** through InvenioRDM's built-in preservation metadata framework
- **Harvard Library standards** compliance via the QDC schema and FADGI-aligned digitisation specifications
- **Terraform IaC** ensures the entire environment can be reproduced identically in Harvard's institutional AWS environment, eliminating single-point-of-failure risks
- **OpenSearch index rebuilds** from the authoritative RDS database, ensuring no permanent dependency on derived indices

---

## 4. Advancing the Strategic AI Vision: RAG & Knowledge Graphs

The NEH grant outlined a strategic vision for coupling **Knowledge Graphs and Large Language Models (LLMs)** via Retrieval-Augmented Generation (RAG) to enable ChatGPT-like capabilities over Turath's curated content.

During this phase, we conducted a comprehensive feasibility study confirming the infrastructure is fully AI-ready. The study tested all six RAG use cases identified in the grant:

| Grant Use Case | Technical Implementation | Verified |
|---------------|-------------------------|---------|
| Question answering | IIIF in-document search returns exact pages | ✅ |
| Text summarization | Page-level text chunks via annotations API | ✅ |
| Knowledge cutoff | Live API serves current, curated chronicle content | ✅ |
| Citation-backed generation | Pixel-level `x,y,w,h` bounding boxes for every word | ✅ |
| Smart searching | HOCR fulltext search returns ranked, relevant records | ✅ |
| Context-aware document linking | Rich Dublin Core metadata enables cross-record context | ✅ |

**Key finding:** The IIIF annotations endpoint returns 11,677 words with bounding-box coordinates from a single 47-page manuscript, entirely via lightweight JSON API calls — no consumer-side PDF parsing or OCR required. Future LLM interfaces can render exact visual citations on manuscript pages, directly addressing the grant's explainability and ethical traceability goals.

**Knowledge Graph readiness:** The structured metadata fields (`turath:creator_arabic`, `turath:subject`, `turath:coverage_spatial`, `turath:coverage_temporal_*`, `turath:relation_*`) provide the entity data required to build Knowledge Graph nodes and edges, enabling the "Knowledge Graphs AND LLMs" strategy described in the grant. The documented REST APIs make this data accessible to any external Knowledge Graph construction pipeline.

---

## 5. Conclusion

This phase of the Turath project has successfully delivered all three CoA digital outputs, fully implemented the FAIR data principles, and established a production-grade, IIIF-compliant, Arabic-optimised repository. The platform goes substantially beyond the out-of-the-box capabilities of InvenioRDM to deliver a purpose-built Arabic digital humanities infrastructure.

The system is operationally stable, documented, tested, and designed to migrate seamlessly to Harvard's institutional AWS infrastructure. The API architecture is verified ready for the grant's next-phase AI vision — Knowledge Graph construction and LLM-powered exploration of the chronicles.
