# Turath InvenioRDM: Master Technical Documentation Index

**Date:** October 26, 2025
**Purpose:** This document serves as the central hub for all technical documentation related to the Turath InvenioRDM project. It points developers, system administrators, and future maintainers to the right resources for setup, customization, APIs, and architecture.

## 1. System Architecture & Extensibility
Documents detailing how the system is designed, how different microservices interact, and how to extend the data models.

*   **[System Architecture & Runbook](./learning/architecture/system_architecture_and_runbook.md):** The master guide detailing the two installation methods (Local vs. Containerized), Docker services, and the ingestion workflow.
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

*   **[AWS Deployment Plan (inveniordm-terraform repo)](../../../inveniordm-terraform/DEPLOYMENT_PLAN.md):** Detailed breakdown of the Terraform modules, networking, and ECS setup.
*   **[CI/CD Migration Guide (inveniordm-terraform repo)](../../../inveniordm-terraform/MIGRATION_CICD_GUIDE.md):** Documentation on the GitHub Actions pipeline that builds and pushes Docker images to GHCR.
*   **[Harvard AWS Migration Plan](./planning/Harvard_AWS_Migration_Plan.md):** Step-by-step runbook for porting the current AWS infrastructure to Harvard's AWS environment.

## 4. Workflows & Scripts
Documentation on the Python scripts used for bulk operations, data ingestion, and testing.

*   **Upload Book Workflow:** Details on `scripts/upload_book.py`, which handles PDF/HOCR uploading, manifest generation, and filesystem syncing.
*   **[Search Robustness Testing](./testing/Search_Robustness_Test_Report.md):** Report and script (`scripts/run_search_tests.py`) validating the integrity of the OpenSearch indexing and Arabic text handling.

## 5. Troubleshooting & Learnings
Deep-dive research notes and debugging sessions.

*   **[ECS Deployment Debugging Session](./learning/deployment-invenio12/learning/aws-deployment/):** Notes on solving uWSGI timeouts, Nginx proxy loops, and health check failures on AWS ECS.
*   **[Mirador Integration Research](./learning/iiif-mirador-multipage/MIRADOR-INTEGRATION-RESEARCH.md):** Deep research on why we chose the "Zenodo Approach" (JS injection via Webpack) over legacy Invenio plugins.
*   **[Filesystem Parent ID Storage](./planning/filesystem-parent-id-storage/master-plan.md):** Why we route files through the `parent_id` rather than the version `record_pid` to ensure stable IIIF URLs across record versions.
