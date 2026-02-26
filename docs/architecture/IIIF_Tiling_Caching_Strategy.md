# IIIF Tiling & Caching Strategy for Turath InvenioRDM

**Date:** October 26, 2025
**Subject:** Recommendations for IIIF Tiling/Caching Configuration for Optimal Performance

## Executive Summary
This document outlines the recommended strategy for handling high-resolution image serving via IIIF in the Turath project. Based on a deep technical study comparing Zenodo's native IIPImage preprocessing architecture against our current Cantaloupe implementation, we recommend **retaining Cantaloupe with an aggressive "Pre-warming" strategy**.

This approach provides the optimal balance between high performance (instant user access) and architectural simplicity (fewer moving parts in the containerized deployment).

## Context: The Challenge of High-Resolution IIIF
Serving large PDFs or high-resolution images via IIIF requires converting the source file into pyramidal tiles. 
- If done **on-the-fly** (when a user opens the viewer), the first user experiences a 2-5 second delay per page as the server extracts the page, scales it, and creates tiles.
- If done **ahead of time** (preprocessing), users get instant access, but the ingestion pipeline becomes significantly more complex.

## Comparison of Approaches

### Approach A: Zenodo's Native Implementation (IIPImage + VIPS)
Zenodo handles this by preprocessing files into `.ptif` (Pyramidal TIFF) files immediately after publication using Celery workers and the Python VIPS library. These `.ptif` files are then served statically via the C++ IIPImage server.

*   **Pros:** True zero-delay for the first viewer. Extremely fast static serving.
*   **Cons:** Highly complex infrastructure. Requires running an additional IIPImage server, managing shared filesystem volumes between Celery workers and the image server, and handling complex state transitions in the database (`init` -> `processing` -> `finished`). It also doubles the storage requirement (storing both the original PDF and the `.ptif` tiles).

### Approach B: Turath's Current Implementation (Cantaloupe On-Demand)
Turath currently uses the Java-based Cantaloupe Image Server. Cantaloupe reads the original PDF and generates tiles on-the-fly when requested, caching the resulting derivative images.

*   **Pros:** Architecturally simple. A single container handles extraction, tiling, and serving. Lower overall storage footprint since it only caches requested derivative sizes.
*   **Cons:** The "First-View Penalty." The first time a user views a page, Cantaloupe must process it, causing a noticeable delay.

## Recommended Strategy: Cantaloupe Pre-Warming

To achieve Zenodo-like performance without adopting its architectural complexity, we recommend implementing a **Cache Pre-warming Strategy** on top of our existing Cantaloupe setup.

### How it Works
1.  **Ingestion:** A book (PDF + HOCR) is uploaded to InvenioRDM.
2.  **File Sync:** The PDF is synced to the `cantaloupe-files` volume.
3.  **Pre-warming Script:** Immediately after the PDF is available to Cantaloupe, a background script automatically hits the IIIF endpoints for all pages of the document at common zoom levels (e.g., full page, 50% zoom).
4.  **Result:** Cantaloupe processes the pages and populates its derivative cache *before* any real user accesses the record. 

### Benefits of this Strategy
- **Instant Access:** Users experience zero delay, identical to Zenodo's approach.
- **Architectural Simplicity:** We do not need to deploy IIPImage, VIPS, or modify the core InvenioRDM Celery task queue. We keep our single, robust Cantaloupe container.
- **Controlled Storage:** Cantaloupe's derivative cache can be configured with a TTL (Time To Live) or maximum size limit, automatically purging rarely accessed tiles to save disk space, unlike static `.ptif` files which exist forever.

## Configuration Recommendations for Cantaloupe

To support this strategy efficiently, the `cantaloupe.properties` file must be optimized:

1.  **Resolver:** Use `FilesystemResolver` pointing directly to the synced PDF directory (using the `parent_id` structure). Do *not* use `HttpResolver` back to the InvenioRDM API, as this creates unnecessary network overhead and authentication hurdles.
2.  **Processor:** Use `PdfBoxProcessor` for PDF extraction.
3.  **Derivative Cache:** 
    *   Enable `FilesystemCache`.
    *   Ensure the cache volume is mounted to persistent storage (e.g., AWS EFS in production) so the cache survives container restarts.
    *   Set `FilesystemCache.TTL` to a reasonable duration (e.g., 30 days) to prevent infinite storage growth.
4.  **Info Cache:** Enable `FilesystemCache` or `HeapCache` for the `info.json` responses to speed up Mirador initialization.

## Next Steps for Implementation
1.  Develop the `prewarm_cantaloupe.py` utility script.
2.  Integrate this script into the end of the `upload_book.py` ingestion pipeline.
3.  Verify the persistent EFS volume mapping for Cantaloupe's derivative cache in the Terraform configuration (`ecs-cantaloupe-service.tf`).
