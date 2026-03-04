# Turath InvenioRDM: Contract Deliverables Mapping

**Last Updated:** March 2026
**Purpose:** Maps every contract deliverable code to actual documentation files for verification and audit purposes.

---

## Phase 1 Deliverables (July–September 2025)

### P1-1.1: CI/CD Pipeline
**Description:** "Stabilize CI/CD Pipeline: Analyze the existing CI/CD setup. Refactor for stability for Harvard AWS environment. Implement basic automated tests. Deliverable: Stabilized, documented CI/CD pipeline."

**Delivered File:** [`deployment/CICD_Pipeline.md`](./deployment/CICD_Pipeline.md)

**Summary:** GitHub Actions pipeline that automatically builds and pushes three Docker images (main app, Nginx frontend, IIIF search service) to GitHub Container Registry on every push to `main`/`develop`. Uses layer caching for efficiency. Integrates with AWS ECS Fargate for deployment.

---

### P1-1.2: Backup & Recovery
**Description:** "Implement Backup & Recovery (Test Host): Establish and test reliable backup and recovery procedures. Deliverable: Documented backup/recovery plan; Functional backup scripts."

**Delivered Files:**
- [`deployment/Backup_Recovery_Plan.md`](./deployment/Backup_Recovery_Plan.md) — Comprehensive plan covering RDS PITR, S3 versioning, OpenSearch rebuild, Terraform-based recovery environment
- [`../Task-2.6-Backup-and-Recovery/scripts/backup_rds_manual.sh`](../Task-2.6-Backup-and-Recovery/scripts/backup_rds_manual.sh) — Manual RDS snapshot script
- [`../Task-2.6-Backup-and-Recovery/scripts/backup_s3_manual.sh`](../Task-2.6-Backup-and-Recovery/scripts/backup_s3_manual.sh) — Manual S3 backup script
- [`../Task-2.6-Backup-and-Recovery/scripts/restore_rds_guide.sh`](../Task-2.6-Backup-and-Recovery/scripts/restore_rds_guide.sh) — RDS restore guide

**Summary:** AWS-native backup strategy using RDS automated backups (7-day PITR), S3 versioning, and Terraform IaC for on-demand recovery environments. Includes a lessons-learned log from a real February 2026 recovery incident.

---

### P1-1.3: Deploy to Test Host
**Description:** "Set up and deploy a functional InvenioRDM instance on a test server. Deliverable: Working InvenioRDM on a test host."

**Delivered:** AWS ECS Fargate deployment via Terraform IaC (see [`deployment/CICD_Pipeline.md`](./deployment/CICD_Pipeline.md) and [`deployment/Backup_Recovery_Plan.md`](./deployment/Backup_Recovery_Plan.md))

**Summary:** Rather than a static "test host" machine, the infrastructure is fully codified in Terraform (`inveniordm-terraform` repository). A test/recovery environment can be spun up on-demand by running `terraform apply` in a new workspace — equivalent to a fresh test host, but reproducible and consistent with production. The live system is operational at `https://invenio.turath-project.com`.

---

### P1-2.1: CoA Metadata Schema & Deposit Form
**Description:** "Work with scholarly team to implement metadata schema for CoA. Develop and iteratively refine deposit form/UI for CoA metadata entry. Deliverable: Functioning deposit form; Documented flexible metadata schema."

**Delivered File:** [`features/CoA_Metadata_Schema.md`](./features/CoA_Metadata_Schema.md)

**Summary:** 20+ custom metadata fields under the `turath:` namespace covering titles, creators, publication details, subjects, language, coverage (temporal/spatial), rights, and identifiers. All fields exposed in the InvenioRDM deposit form with labels and descriptions. Full vocabulary-controlled fields for creators, subjects, languages, and more.

---

### P1-2.2: UI-Driven Ingestion Workflow for CoA (with HOCR for Search)
**Description:** "Develop a UI-driven workflow for non-technical users to upload CoA materials. Ensure HOCR files are correctly associated for search indexing. Deliverable: UI-driven ingestion workflow for CoA."

**Delivered File:** [`workflows/Ingestion_Workflow.md`](./workflows/Ingestion_Workflow.md)

**Summary:** Two-pathway ingestion system: (1) The extended InvenioRDM web deposit form allows curators to upload PDFs and HOCR files directly through the browser alongside metadata; (2) A `batch_upload_books.py` script for bulk ingestion of pre-processed collections. Both pathways trigger the Celery-based HOCR indexing pipeline and IIIF manifest generation automatically on publish.

---

### P1-3.1: Foundational HOCR Full-Text Search
**Description:** "Configure search service to search through HOCR/PageXML content. Implement script to combine HOCR content and allow full-text queries. Deliverable: Initial HOCR full-text search for CoA implemented and functional."

**Delivered File:** [`features/HOCR_Fulltext_Search.md`](./features/HOCR_Fulltext_Search.md)

**Summary:** Custom `turath:fulltext` OpenSearch field aggregates all OCR text from a book's HOCR files. Arabic text analyzer with stemming and stop-word removal. Full-text phrase and word search available via the standard InvenioRDM API (`/api/records?q=custom_fields.turath\:fulltext:"phrase"`).

---

### P1-3.2: Mirador Preview
**Description:** "Basic Mirador image preview for CoA functional. IIIF manifest generation upon user upload for CoA items, ensuring Mirador compatibility." (Phase 1 Milestone)

**Delivered Files:**
- [`features/Mirador_Text_Overlay.md`](./features/Mirador_Text_Overlay.md) — Covers both Phase 1 basic preview and Phase 2 text overlay
- Live at [`https://invenio.turath-project.com`](https://invenio.turath-project.com) — Mirador 3 viewer operational on all records

**Summary:** Mirador 3 viewer integrated with IIIF manifest generation. Multi-page PDF records are mapped to IIIF canvases with page navigation and zoom. Manifests are generated automatically on record publish via the Celery pipeline, ensuring every uploaded CoA item is immediately previewable in the browser viewer.

---

### P1-3.3: Cantaloupe Review
**Description:** "Re-evaluate the current Cantaloupe integration. Identify and implement initial optimizations for performance or stability related to CoA image display. Deliverable: Report on Cantaloupe integration status."

**Delivered File:** [`status/Cantaloupe_Integration_Review.md`](./status/Cantaloupe_Integration_Review.md)

**Summary:** Report detailing the stability of the FilesystemSource integration and the critical implementation of FilesystemCache for derivatives, which reduced cached load times to <0.5s. Identifies pre-warming as the next key optimisation.

---

## Phase 2 Deliverables (October–December 2025)

### P2-1.1: Enhanced HOCR Full-Text Search ("Central Search Service")
**Description:** "Elasticsearch configuration for HOCR content: refine indexing strategies, improve query parsing. Enhance the search UI/UX with facets. Deliverable: Enhanced HOCR full-text search with improved UI/UX."

**Delivered File:** [`features/HOCR_Fulltext_Search.md`](./features/HOCR_Fulltext_Search.md) (Phase 2 section)

**Summary:** Arabic OpenSearch analyzer with stemming. Dual-mode search UI (metadata/fulltext toggle). Wildcard metadata matching. Search result highlighting with HOCR snippets. Faceted filtering by resource type, language, subject, and date. `ExcludeFulltextSourceParam` optimisation reduces response payload by ~97%.

---

### P2-2.1: Enhanced Mirador Preview with Text Overlay
**Description:** "Integrate textoverlay-mirador (or similar) to display HOCR/PageXML text overlaid on scanned images within the existing Mirador viewer. Deliverable: Mirador with functional text overlay."

**Delivered File:** [`features/Mirador_Text_Overlay.md`](./features/Mirador_Text_Overlay.md)

**Summary:** `textoverlay-mirador` plugin bundled into the custom `mirador.min.js`. Renders all OCR words as selectable, hoverable HTML elements positioned over the scanned image. Complemented by IIIF Content Search API 1.0 integration (search microservice on port 5001), enabling in-viewer search with page-jump and bounding-box highlighting.

---

### P2-3.1: Refine User Roles & Permissions
**Description:** "Refine user roles in InvenioRDM for clarity and access control. Deliverable: Updated user roles configuration."

**Delivered Files:**
- [`../P2-3.1-User-Roles-Permissions/P2-3.1_user_roles_permissions.md`](../P2-3.1-User-Roles-Permissions/P2-3.1_user_roles_permissions.md) — Role definitions and permission matrix
- [`../P2-3.1-User-Roles-Permissions/P2-3.1_proof/`](../P2-3.1-User-Roles-Permissions/P2-3.1_proof/) — Supporting evidence
- [`../P2-3.1-User-Roles-Permissions/create_curator_user.py`](../P2-3.1-User-Roles-Permissions/create_curator_user.py) — Curator user creation script
- [`../P2-3.1-User-Roles-Permissions/setup_production_roles.py`](../P2-3.1-User-Roles-Permissions/setup_production_roles.py) — Production role setup script

**Summary:** Three-tier role model: System Administrator (full platform access), Curator (content ingestion and publication), Public User (read-only access). Includes permission matrix table and setup scripts.

---

### P2-3.2: IIIF Tiling/Caching
**Description:** "Investigate and document IIIF tiling/caching configuration for performance. Deliverable: Recommendations for IIIF tiling/caching strategy."

**Delivered File:** [`architecture/IIIF_Tiling_Caching_Strategy.md`](./architecture/IIIF_Tiling_Caching_Strategy.md)

**Summary:** Comprehensive analysis comparing Zenodo's IIPImage preprocessing approach vs. Turath's Cantaloupe on-demand tiling, with recommendation for cache pre-warming strategy to achieve optimal performance.

---

### P2-4.1: Extensibility Docs
**Description:** "Document metadata & search framework flexibility and how it can be configured for future initiatives. Deliverable: Documentation detailing framework design and configurability."

**Delivered File:** [`architecture/Extensibility_Framework.md`](./architecture/Extensibility_Framework.md)

**Summary:** Complete guide to InvenioRDM's extensibility framework covering custom metadata fields, OpenSearch mapping overrides, and React UI component customisation with real implementation examples.

---

## Phase 3 Deliverables (January–February 2026)

### P3-1.1: UI "Look and Feel" Customisation
**Description:** "Implement agreed-upon minor branding changes (logo, main colors). Deliverable: Themed InvenioRDM instance."

**Delivered File:** [`features/UI_Theming.md`](./features/UI_Theming.md)

**Summary:** Turath brand logos and tagline implemented in header and homepage. Custom homepage with sidebar layout, bilingual search, and collection navigation. Custom Semantic UI LESS overrides. React search component overrides for metadata/fulltext dual-mode search.

---

### P3-2.1: API Documentation
**Description:** "Document key InvenioRDM REST APIs for data search, retrieval, and ingestion. Deliverable: Developer documentation for selected REST APIs."

**Delivered Files:**
- [`APIs/search.md`](./APIs/search.md) — Search API including custom HOCR full-text search
- [`APIs/files.md`](./APIs/files.md) — File upload/download workflow
- [`APIs/records.md`](./APIs/records.md) — Metadata record retrieval
- [`APIs/iiif.md`](./APIs/iiif.md) — IIIF Search, Autocomplete & Annotations API
- [`APIs/README.md`](./APIs/README.md) — API overview and quick start

**Summary:** Comprehensive REST API documentation covering all major operations: standard metadata search, HOCR full-text search, record CRUD, file management, and the custom IIIF search/annotations microservice.

---

### P3-2.2: RAG Feasibility Test
**Description:** "Test if the documented APIs can successfully provide data to a hypothetical external RAG pipeline. Deliverable: Report on API readiness for RAG."

**Delivered Files:**
- [`APIs/RAG_Feasibility_Report.md`](./APIs/RAG_Feasibility_Report.md) — Test results and analysis
- [`../scripts/rag_feasibility_test.py`](../scripts/rag_feasibility_test.py) — Executable test script

**Summary:** Proof-of-concept demonstrating successful extraction of metadata and page-level OCR text via REST APIs, confirming system readiness for LLM/RAG integration.

---

### P3-3.1: Technical Documentation Suite
**Description:** "Consolidate and finalize all technical documentation. Deliverable: Finalized technical documentation suite."

**Delivered File:** [`MASTER_TECH_DOCS_INDEX.md`](./MASTER_TECH_DOCS_INDEX.md)

**Summary:** Central navigation hub linking all technical documentation organised by category (Architecture, APIs, Deployment, Features, Workflows, Testing). Acts as the consolidated entry point for the entire documentation suite.

---

### P3-3.2: System Testing
**Description:** "Final testing round for all features, focus on search robustness. Deliverable: Test summary report."

**Delivered Files:**
- [`testing/Search_Robustness_Test_Report.md`](./testing/Search_Robustness_Test_Report.md) — Test results report
- [`../scripts/run_search_tests.py`](../scripts/run_search_tests.py) — Executable test suite

**Summary:** Comprehensive test report covering 6 search test cases (metadata search English/Arabic, HOCR phrase/word search, pagination, error handling). All tests passing with 100% pass rate.

---

### P3-3.3: AWS Migration Plan
**Description:** "Document steps, considerations, and estimated effort for migrating InvenioRDM to Harvard AWS. Deliverable: AWS migration planning document."

**Delivered File:** [`planning/Harvard_AWS_Migration_Plan.md`](./planning/Harvard_AWS_Migration_Plan.md)

**Summary:** Detailed 5-phase migration runbook with effort estimates (1-2 weeks), covering infrastructure provisioning via Terraform, data migration (RDS + EFS), and validation procedures.

---

### P3-3.4: NEH Report Input
**Description:** "Provide all necessary technical details and summaries for NEH grant report. Deliverable: Technical input for NEH report."

**Delivered File:** [`status/NEH_Technical_Report_Summary.md`](./status/NEH_Technical_Report_Summary.md)

**Summary:** Executive-level technical summary highlighting major achievements (IIIF integration, Arabic full-text search, cloud infrastructure, RAG-readiness) suitable for grant reporting to non-technical stakeholders.

---

## Verification Checklist

### Phase 1
- [x] P1-1.1: CI/CD Pipeline — ✅ Complete
- [x] P1-1.2: Backup & Recovery — ✅ Complete
- [x] P1-1.3: Deploy to Test Host — ✅ Complete (AWS/Terraform environment)
- [x] P1-2.1: CoA Metadata Schema & Deposit Form — ✅ Complete
- [x] P1-2.2: UI-Driven Ingestion Workflow — ✅ Complete
- [x] P1-3.1: Foundational HOCR Full-Text Search — ✅ Complete
- [x] P1-3.2: Mirador Preview — ✅ Complete
- [x] P1-3.3: Cantaloupe Review — ✅ Complete

### Phase 2
- [x] P2-1.1: Enhanced HOCR Full-Text Search — ✅ Complete
- [x] P2-2.1: Mirador Text Overlay — ✅ Complete
- [x] P2-3.1: User Roles & Permissions — ✅ Complete
- [x] P2-3.2: IIIF Tiling/Caching — ✅ Complete
- [x] P2-4.1: Extensibility Docs — ✅ Complete

### Phase 3
- [x] P3-1.1: UI Theming — ✅ Complete
- [x] P3-2.1: API Documentation — ✅ Complete
- [x] P3-2.2: RAG Feasibility Test — ✅ Complete
- [x] P3-3.1: Tech Docs Suite — ✅ Complete
- [x] P3-3.2: System Testing — ✅ Complete
- [x] P3-3.3: AWS Migration Plan — ✅ Complete
- [x] P3-3.4: NEH Report Input — ✅ Complete

**All 20 contractual deliverables fulfilled and documented.**
