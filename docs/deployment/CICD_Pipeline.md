# CI/CD Pipeline Documentation

**Deliverable:** P1-1.1 — Stabilized, documented CI/CD pipeline
**Phase:** 1 (July–September 2025)
**Date:** March 2026
**Status:** Operational

---

## Overview

The Turath InvenioRDM CI/CD pipeline is implemented using **GitHub Actions** and automatically builds, tags, and publishes three Docker images to the **GitHub Container Registry (GHCR)** on every push to the `main` or `develop` branches. This ensures that the latest application code is always available for deployment to AWS ECS Fargate with zero manual steps.

---

## Pipeline Architecture

```
Developer pushes to main/develop
            │
            ▼
   GitHub Actions triggered
            │
    ┌───────┴──────────┐
    │                  │                 │
    ▼                  ▼                 ▼
Main App Image    Frontend Image    Search Service Image
(InvenioRDM +    (Nginx reverse     (IIIF search +
 Turath site)      proxy)            annotations)
    │                  │                 │
    └───────┬──────────┘                 │
            ▼                            ▼
  ghcr.io/alaabarazi/             ghcr.io/alabarazi/
  turath-rdm:{tag}                turath-search-service:{tag}
            │
            ▼
    AWS ECS Fargate pulls
    updated images on next
    force-deployment
```

---

## Trigger Conditions

| Event | Branch/Tag | Action |
|-------|-----------|--------|
| `push` | `main` | Build + Push all 3 images |
| `push` | `develop` | Build + Push all 3 images |
| `push` | `v*` tag (e.g. `v1.2.0`) | Build + Push with semver tags |
| `pull_request` | `main` or `develop` | Build only (no push) |

---

## Images Built

### 1. Main Application Image
- **Registry path:** `ghcr.io/alaabarazi/turath-rdm:{tag}`
- **Dockerfile:** `./Dockerfile` (root of `turath-rdm` repo)
- **Contents:** InvenioRDM + all Turath customisations (custom fields, search options, IIIF patches, templates, assets)

### 2. Frontend (Nginx) Image
- **Registry path:** `ghcr.io/alaabarazi/turath-rdm-frontend:{tag}`
- **Dockerfile:** `./docker/nginx/Dockerfile`
- **Contents:** Nginx reverse proxy configuration for production HTTPS routing

### 3. IIIF Search Service Image
- **Registry path:** `ghcr.io/alabarazi/turath-search-service:{tag}`
- **Dockerfile:** `./services/search_service/Dockerfile`
- **Contents:** Flask microservice for IIIF Content Search API and text overlay annotations

---

## Image Tagging Strategy

Each image receives multiple tags per build:

| Tag format | Example | Used for |
|-----------|---------|----------|
| Branch name | `develop`, `main` | Latest build on that branch |
| Pull Request | `pr-42` | Traceability for review |
| Semver | `1.2.0`, `1.2` | Formal releases |
| Git SHA | `sha-a1b2c3d` | Exact commit traceability |

---

## Build Optimisation

The pipeline uses **GitHub Actions cache** (`type=gha`) for Docker layer caching:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

This dramatically reduces build times for subsequent pushes by reusing unchanged layers (e.g., base Python image, dependency installation).

---

## Pre-built Third-Party Images (No Custom Build)

The following services are used as-is from upstream and are not built by this pipeline:

| Service | Image |
|---------|-------|
| Cantaloupe IIIF Image Server | `edirom/cantaloupe:latest` |
| PostgreSQL | `postgres:14.13` |
| OpenSearch | `opensearchproject/opensearch:2.17.1` |
| Redis (ElastiCache) | `redis:7` |
| RabbitMQ (Amazon MQ) | `rabbitmq:3-management` |

---

## Deployment to AWS ECS

The CI/CD pipeline handles **image publishing only**. Deployment to AWS ECS Fargate is a separate step:

1. After the pipeline pushes a new image, Terraform is used to update ECS task definitions.
2. A `force-new-deployment` command picks up the new image:

```bash
# Update ECS service to pull the latest image
aws ecs update-service \
  --cluster invenio-default-cluster \
  --service web-ui \
  --force-new-deployment

aws ecs update-service \
  --cluster invenio-default-cluster \
  --service web-api \
  --force-new-deployment

aws ecs update-service \
  --cluster invenio-default-cluster \
  --service search-service \
  --force-new-deployment
```

3. Monitor rollout:
```bash
aws ecs describe-services \
  --cluster invenio-default-cluster \
  --services web-ui \
  --query 'services[0].deployments[0].[status,rolloutState,runningCount]'
```

---

## Secrets & Authentication

- **GHCR authentication** uses the automatic `GITHUB_TOKEN` provided by GitHub Actions (no manual secret required).
- **AWS ECS pull authentication** uses a Secrets Manager secret (`ghcr_credentials`) containing the GitHub PAT. ECS tasks reference this secret via `repositoryCredentials` in the task definition.

---

## Repository Structure

```
turath-rdm/
├── .github/
│   └── workflows/
│       └── docker-publish.yml   ← CI/CD pipeline definition
├── Dockerfile                   ← Main application image
├── docker/
│   └── nginx/
│       └── Dockerfile           ← Frontend (Nginx) image
└── services/
    └── search_service/
        └── Dockerfile           ← IIIF Search Service image
```
