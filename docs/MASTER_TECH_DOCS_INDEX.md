# Turath InvenioRDM: Master Technical Documentation Index

**Deliverable:** P3-3.1 — Technical Documentation Suite
**Last Updated:** March 2026
**Purpose:** Central hub for all technical documentation. Points developers, system administrators, and future maintainers to the right resources for setup, customisation, APIs, and architecture.

---

## Quick Reference

- **[DELIVERABLES_MAPPING.md](./DELIVERABLES_MAPPING.md)** — Maps every contract deliverable code (P1-1.1 through P3-3.4) to its documentation file for verification
- **Live platform:** `https://invenio.turath-project.com`
- **IIIF Search Service:** `https://invenio.turath-project.com:5001`

---

## 1. System Architecture & Extensibility

*How the system is designed, how microservices interact, and how to extend data models and search.*

- **[Extensibility Framework](./architecture/Extensibility_Framework.md)** *(P2-4.1)* — How to add custom metadata fields, modify OpenSearch indexing (Arabic analyzers), and override React frontend components
- **[Cantaloupe Integration Review](./status/Cantaloupe_Integration_Review.md)** *(P1-3.1)* — Stability report and optimisations for the Cantaloupe IIIF image server
- **[IIIF Tiling & Caching Strategy](./architecture/IIIF_Tiling_Caching_Strategy.md)** *(P2-3.2)* — Decision to use Cantaloupe with cache pre-warming over complex VIPS/IIPImage preprocessing

---

## 2. APIs & Integrations

*Documentation for interacting with the Turath instance programmatically.*

- **[API Overview](./APIs/README.md)** — Central index for all REST APIs, quick start examples
- **[Records API](./APIs/records.md)** — Endpoints for retrieving, creating, and publishing metadata records
- **[Search API](./APIs/search.md)** *(P3-2.1)* — Standard Lucene queries and custom HOCR full-text search syntax
- **[Files API](./APIs/files.md)** — Workflows for uploading and downloading files
- **[IIIF Search & Annotations API](./APIs/iiif.md)** *(P3-2.1)* — IIIF Content Search API (in-viewer search + autocomplete) and the Annotations endpoint powering text overlay
- **[RAG Feasibility Report](./APIs/RAG_Feasibility_Report.md)** *(P3-2.2)* — Proof-of-concept demonstrating APIs can feed an external LLM/RAG pipeline

---

## 3. Deployment & DevOps (AWS)

*Guides for deploying the infrastructure using Terraform and CI/CD pipelines.*

- **[CI/CD Pipeline](./deployment/CICD_Pipeline.md)** *(P1-1.1)* — GitHub Actions pipeline: three Docker images built and pushed to GHCR on every push; deployment to AWS ECS Fargate
- **[Backup & Recovery Plan](./deployment/Backup_Recovery_Plan.md)** *(P1-1.2)* — RDS automated backups (7-day PITR), S3 versioning, OpenSearch rebuild procedure, and step-by-step disaster recovery runbook
- **[Harvard AWS Migration Plan](./planning/Harvard_AWS_Migration_Plan.md)** *(P3-3.3)* — Step-by-step runbook for porting the current AWS infrastructure to Harvard's AWS environment
- **[NEH Technical Report Summary](./status/NEH_Technical_Report_Summary.md)** *(P3-3.4)* — Executive summary of technical achievements for grant reporting

---

## 4. Features

*Deep-dives into each major implemented feature.*

- **[CoA Metadata Schema](./features/CoA_Metadata_Schema.md)** *(P1-2.1)* — The complete 20+ field metadata schema for the Chronicles of Arabia, including field definitions, controlled vocabularies, and deposit form configuration
- **[HOCR Full-Text Search](./features/HOCR_Fulltext_Search.md)** *(P1-2.3, P2-1.1)* — Two-layer search: record-level full-text (OpenSearch) and within-document word highlighting (IIIF Search). Arabic analyzer, search UI, facets, and performance optimisations
- **[Mirador Text Overlay & In-Viewer Search](./features/Mirador_Text_Overlay.md)** *(P2-2.1)* — Text overlay plugin rendering OCR words as selectable elements over scanned images; IIIF Content Search API integration for in-Mirador search with page-jump
- **[UI Theming & Branding](./features/UI_Theming.md)** *(P3-1.1)* — Turath logos, custom homepage, header customisation, Semantic UI LESS overrides, and React search component overrides
- **[User Roles & Permissions](../P2-3.1-User-Roles-Permissions/P2-3.1_user_roles_permissions.md)** *(P2-3.1)* — Three-tier role model: System Administrator, Curator, Public User

---

## 5. Workflows & Scripts

*Documentation on ingestion workflows, bulk operations, and data management.*

- **[Data Ingestion Workflow](./workflows/Ingestion_Workflow.md)** *(P1-2.2)* — Two-pathway ingestion: web UI deposit form for curators; batch upload script for technical ingestion of pre-processed collections. Covers HOCR association, IIIF manifest generation, and post-ingestion verification

---

## 6. Testing

- **[Search Robustness Test Report](./testing/Search_Robustness_Test_Report.md)** *(P3-3.2)* — Report and executable script (`scripts/run_search_tests.py`) validating OpenSearch indexing and Arabic full-text search. 100% pass rate across 6 test cases

---

## Infrastructure Overview

| Component | Technology | Notes |
|-----------|-----------|-------|
| Application Framework | InvenioRDM | Python/Flask + React frontend |
| Container Orchestration | AWS ECS Fargate | Web UI, Web API, Celery, Search Service, Cantaloupe |
| Database | Amazon RDS PostgreSQL 14 | 7-day automated backups + PITR |
| Search Engine | Amazon OpenSearch | Custom Arabic analyzer |
| Cache | Amazon ElastiCache (Redis) | Session cache, task queue results |
| Message Queue | Amazon MQ (RabbitMQ) | Celery task broker |
| File Storage | Amazon S3 + EFS | S3 for records/files, EFS for HOCR and Cantaloupe cache |
| Image Server | Cantaloupe IIIF | Filesystem source + derivative cache |
| IaC | Terraform | Full infrastructure codified in `inveniordm-terraform` repo |
| CI/CD | GitHub Actions | Builds 3 Docker images on push to main/develop |
| SSL/DNS | AWS ACM + Route53 | Automatic certificate renewal |
