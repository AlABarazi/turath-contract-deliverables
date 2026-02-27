# Turath InvenioRDM: Master Technical Documentation Index

**Date:** October 26, 2025
**Purpose:** This document serves as the central hub for all technical documentation related to the Turath InvenioRDM project deliverables. It points developers, system administrators, and future maintainers to the right resources for setup, customization, APIs, and architecture.

## 1. System Architecture & Extensibility
Documents detailing how the system is designed, how different microservices interact, and how to extend the data models.

*   **[Extensibility Framework](./architecture/Extensibility_Framework.md):** Guide on how to add new metadata custom fields, modify OpenSearch indexing (e.g., Arabic analyzers), and override React frontend components.
*   **[IIIF Tiling & Caching Strategy](./architecture/IIIF_Tiling_Caching_Strategy.md):** Details our decision to use Cantaloupe with cache pre-warming over complex VIPS/IIPImage preprocessing.

## 2. APIs & Integrations
Documentation for interacting with the Turath instance programmatically.

*   **[API Overview](./APIs/README.md):** Central index for all REST APIs.
*   **[Records API](./APIs/records.md):** Endpoints for retrieving, creating, and publishing metadata records.
*   **[Search API](./APIs/search.md):** Details on standard Lucene queries and our custom HOCR full-text search syntax.
*   **[Files API](./APIs/files.md):** Workflows for uploading and downloading files.
*   **[IIIF API](./APIs/iiif.md):** Information on the Presentation API (Manifests) and the custom IIIF Search/Annotations microservice (Port 5001).
*   **[RAG Feasibility Report](./APIs/RAG_Feasibility_Report.md):** A proof-of-concept demonstrating how our APIs can feed an external LLM/RAG pipeline with clean text and metadata.

## 3. Deployment & DevOps (AWS)
Guides for deploying the infrastructure using Terraform and CI/CD pipelines.

*   **[Harvard AWS Migration Plan](./planning/Harvard_AWS_Migration_Plan.md):** Step-by-step runbook for porting the current AWS infrastructure to Harvard's AWS environment.
*   **[NEH Technical Report Summary](./status/NEH_Technical_Report_Summary.md):** Executive summary of technical achievements, scalability, and AI readiness for grant reporting.

## 4. Workflows & Scripts
Documentation on the Python scripts used for bulk operations, data ingestion, and testing.

*   **[Search Robustness Testing](./testing/Search_Robustness_Test_Report.md):** Report and script (`scripts/run_search_tests.py`) validating the integrity of the OpenSearch indexing and Arabic text handling.

*(Note: Internal development runbooks, architectural decision records, and raw research notes are maintained in the private project repository and are not included in this formal deliverable suite.)*
