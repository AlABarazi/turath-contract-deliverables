# Turath InvenioRDM: Technical Documentation & Contract Deliverables

**Project:** Turath Digital Archive Platform
**Contract Period:** July 2025 – March 2026 (8 Months)
**Format:** Markdown Documentation + Executable Test Scripts

---

## Overview

This repository contains the complete technical documentation suite for the Turath InvenioRDM platform, fulfilling all Phase 1, Phase 2, and Phase 3 contract deliverables. The documentation covers CI/CD, backup/recovery, metadata schema, ingestion workflows, HOCR full-text search, IIIF/Mirador integration, UI theming, API specifications, deployment, testing, and migration planning.

## Start Here

- **[DELIVERABLES_MAPPING.md](./docs/DELIVERABLES_MAPPING.md)** — Maps every contract deliverable code (P1-1.1 through P3-3.4) to its documentation file. Start here for verification.
- **[MASTER_TECH_DOCS_INDEX.md](./docs/MASTER_TECH_DOCS_INDEX.md)** — Central hub linking all technical documentation by category.

---

## Deliverables Overview

### Phase 1 (July–September 2025)

| Code | Deliverable | File |
|------|-------------|------|
| P1-1.1 | ✅ CI/CD Pipeline | [`docs/deployment/CICD_Pipeline.md`](./docs/deployment/CICD_Pipeline.md) |
| P1-1.2 | ✅ Backup & Recovery Plan + Scripts | [`docs/deployment/Backup_Recovery_Plan.md`](./docs/deployment/Backup_Recovery_Plan.md) |
| P1-1.3 | ✅ Deployed Environment (Terraform/AWS) | See CI/CD + Backup docs |
| P1-2.1 | ✅ CoA Metadata Schema & Deposit Form | [`docs/features/CoA_Metadata_Schema.md`](./docs/features/CoA_Metadata_Schema.md) |
| P1-2.2 | ✅ Ingestion Workflow (HOCR for Search) | [`docs/workflows/Ingestion_Workflow.md`](./docs/workflows/Ingestion_Workflow.md) |
| P1-2.3 | ✅ Foundational HOCR Full-Text Search | [`docs/features/HOCR_Fulltext_Search.md`](./docs/features/HOCR_Fulltext_Search.md) |
| P1-3.1 | ✅ Cantaloupe Integration Review | [`docs/status/Cantaloupe_Integration_Review.md`](./docs/status/Cantaloupe_Integration_Review.md) |

### Phase 2 (October–December 2025)

| Code | Deliverable | File |
|------|-------------|------|
| P2-1.1 | ✅ Enhanced HOCR Search + UI/UX | [`docs/features/HOCR_Fulltext_Search.md`](./docs/features/HOCR_Fulltext_Search.md) |
| P2-2.1 | ✅ Mirador Text Overlay | [`docs/features/Mirador_Text_Overlay.md`](./docs/features/Mirador_Text_Overlay.md) |
| P2-3.1 | ✅ User Roles & Permissions | [`P2-3.1-User-Roles-Permissions/P2-3.1_user_roles_permissions.md`](./P2-3.1-User-Roles-Permissions/P2-3.1_user_roles_permissions.md) |
| P2-3.2 | ✅ IIIF Tiling/Caching Strategy | [`docs/architecture/IIIF_Tiling_Caching_Strategy.md`](./docs/architecture/IIIF_Tiling_Caching_Strategy.md) |
| P2-4.1 | ✅ Extensibility Framework Docs | [`docs/architecture/Extensibility_Framework.md`](./docs/architecture/Extensibility_Framework.md) |

### Phase 3 (January–February 2026)

| Code | Deliverable | File |
|------|-------------|------|
| P3-1.1 | ✅ UI Theming & Branding | [`docs/features/UI_Theming.md`](./docs/features/UI_Theming.md) |
| P3-2.1 | ✅ API Documentation | [`docs/APIs/`](./docs/APIs/) (records, search, files, IIIF) |
| P3-2.2 | ✅ RAG Feasibility Test | [`docs/APIs/RAG_Feasibility_Report.md`](./docs/APIs/RAG_Feasibility_Report.md) |
| P3-3.1 | ✅ Technical Documentation Suite | [`docs/MASTER_TECH_DOCS_INDEX.md`](./docs/MASTER_TECH_DOCS_INDEX.md) |
| P3-3.2 | ✅ System Testing Report | [`docs/testing/Search_Robustness_Test_Report.md`](./docs/testing/Search_Robustness_Test_Report.md) |
| P3-3.3 | ✅ AWS Migration Plan | [`docs/planning/Harvard_AWS_Migration_Plan.md`](./docs/planning/Harvard_AWS_Migration_Plan.md) |
| P3-3.4 | ✅ NEH Report Input | [`docs/status/NEH_Technical_Report_Summary.md`](./docs/status/NEH_Technical_Report_Summary.md) |

**All 19 contract deliverables fulfilled and documented.**

---

## Repository Structure

```
turath-contract-deliverables/
├── README.md                                    ← This file
├── docs/
│   ├── DELIVERABLES_MAPPING.md                  ← Contract verification map (all deliverables)
│   ├── MASTER_TECH_DOCS_INDEX.md                ← Navigation hub
│   ├── APIs/
│   │   ├── README.md                            ← API overview
│   │   ├── records.md                           ← Records API
│   │   ├── search.md                            ← Search API (HOCR + metadata)
│   │   ├── files.md                             ← Files API
│   │   ├── iiif.md                              ← IIIF Search & Annotations API
│   │   └── RAG_Feasibility_Report.md            ← RAG test results
│   ├── architecture/
│   │   ├── Extensibility_Framework.md           ← Metadata & search extensibility
│   │   └── IIIF_Tiling_Caching_Strategy.md      ← Cantaloupe strategy
│   ├── deployment/
│   │   ├── CICD_Pipeline.md                     ← GitHub Actions CI/CD
│   │   └── Backup_Recovery_Plan.md              ← RDS/S3 backup + recovery runbook
│   ├── features/
│   │   ├── CoA_Metadata_Schema.md               ← 20+ custom metadata fields
│   │   ├── HOCR_Fulltext_Search.md              ← HOCR search (foundational + enhanced)
│   │   ├── Mirador_Text_Overlay.md              ← Text overlay + in-viewer search
│   │   └── UI_Theming.md                        ← Branding & UI customisation
│   ├── workflows/
│   │   └── Ingestion_Workflow.md                ← CoA ingestion (UI + batch)
│   ├── planning/
│   │   └── Harvard_AWS_Migration_Plan.md        ← Migration runbook
│   ├── testing/
│   │   └── Search_Robustness_Test_Report.md     ← System test results
│   └── status/
│       ├── Cantaloupe_Integration_Review.md     ← Cantaloupe review
│       └── NEH_Technical_Report_Summary.md      ← NEH grant input
├── P2-3.1-User-Roles-Permissions/
│   ├── P2-3.1_user_roles_permissions.md
│   └── ...
├── Task-2.6-Backup-and-Recovery/
│   ├── Backup_Recovery_Plan.md
│   └── scripts/
│       ├── backup_rds_manual.sh
│       ├── backup_s3_manual.sh
│       └── restore_rds_guide.sh
└── scripts/
    ├── rag_feasibility_test.py                  ← RAG API test
    └── run_search_tests.py                      ← Search robustness tests
```

---

## Running Test Scripts

```bash
# Install dependencies
pip install requests urllib3

# RAG Feasibility Test
python scripts/rag_feasibility_test.py

# Search Robustness Tests
python scripts/run_search_tests.py
```

*Update the `BASE_URL` variable in each script to point to your InvenioRDM instance.*
