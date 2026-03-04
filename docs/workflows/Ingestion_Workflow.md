# Data Ingestion Workflow

**Deliverable:** P1-2.2 — User-friendly data ingestion workflow for CoA (with HOCR processing for search)
**Phase:** 1 (July–September 2025)
**Date:** March 2026
**Status:** Operational

---

## Overview

The Turath ingestion workflow supports uploading *Chronicles of Arabia* (CoA) materials — scanned PDF books and their associated HOCR (HTML-based OCR) files — into the InvenioRDM repository. The workflow automatically associates HOCR content for full-text search indexing and generates IIIF manifests for the Mirador viewer.

Two complementary pathways are provided:

| Pathway | Who | When |
|---------|-----|------|
| **Web UI deposit form** | Curators / researchers | Single records, metadata entry, one-off uploads |
| **Batch upload script** | Technical curators | Bulk ingestion of pre-processed book collections |

---

## Pathway 1: Web UI Deposit Form

The InvenioRDM deposit form has been extended with the full Turath custom metadata schema. Any authenticated user with the **Curator** role can submit new records through the browser.

### Step-by-Step

1. **Log in** at `https://invenio.turath-project.com/login/`
2. Navigate to **New Upload** (`/uploads/new`)
3. **Fill in metadata** using the Turath-specific fields (see [CoA Metadata Schema](../features/CoA_Metadata_Schema.md) for field definitions):
   - Title, Alternative Title, Creator, Publisher
   - Date, Language, Subject, Description
   - Rights, Coverage (temporal and spatial), etc.
4. **Upload files** in the Files section:
   - Upload the **PDF** (scanned book)
   - Upload all **HOCR files** named `001.hocr`, `002.hocr`, … (one per scanned page)
5. Click **Save draft** → **Publish**

### HOCR Association for Search

Upon publication, a Celery background task runs the HOCR indexing pipeline:

```
Record published
      │
      ▼
  Celery worker triggered (via InvenioRDM signals)
      │
      ▼
  fulltext.py: extract_hocr_text(parent_id)
      │   reads all *.hocr files from EFS mount
      │   parses ocrx_word spans with BeautifulSoup
      │
      ▼
  custom_fields.turath:fulltext updated in OpenSearch
      │
      ▼
  Record is now full-text searchable
```

### IIIF Manifest Generation

IIIF manifests are generated dynamically on request:
- When Mirador loads a record, InvenioRDM calls the manifest endpoint
- The manifest lists all uploaded image pages as IIIF canvases
- The IIIF Search Service URL is embedded in the manifest, enabling in-viewer search

---

## Pathway 2: Batch Upload Script (Technical Curators)

For bulk ingestion of pre-processed book collections, the `batch_upload_books.py` script provides an automated pipeline.

### Prerequisites

- Python 3.9+ with the InvenioRDM virtual environment activated
- A valid API token (see `scripts/create_api_token.md`)
- Book directory structure as described below

### Expected Directory Structure

```
renamed_books/
├── 001_تاريخ_نجد/
│   ├── 001_تاريخ_نجد.pdf      ← scanned book PDF
│   ├── metadata.json           ← Turath custom metadata
│   └── hocr/
│       ├── 001.hocr
│       ├── 002.hocr
│       └── ...
├── 002_كتاب_آخر/
│   └── ...
```

### `metadata.json` Format

```json
{
  "turath:title": "تاريخ نجد",
  "turath:alternative_title": ["History of Najd"],
  "turath:creator_arabic": ["المؤلف الأول"],
  "turath:date": "1920",
  "turath:language": [{"id": "ara"}],
  "turath:description": ["وصف الكتاب هنا"]
}
```

### Running the Script

**Dry run (check without uploading):**
```bash
.venv/bin/python scripts/batch_upload_books.py \
  --books-root "/path/to/renamed_books" \
  --base-url https://invenio.turath-project.com \
  --include-hocr \
  --book-ids "001_تاريخ_نجد" \
  --dry-run
```

**Upload specific books:**
```bash
.venv/bin/python scripts/batch_upload_books.py \
  --books-root "/path/to/renamed_books" \
  --base-url https://invenio.turath-project.com \
  --include-hocr \
  --book-ids "001_تاريخ_نجد" "003_تحفة_المشتاق"
```

**Upload all books:**
```bash
.venv/bin/python scripts/batch_upload_books.py \
  --books-root "/path/to/renamed_books" \
  --base-url https://invenio.turath-project.com \
  --include-hocr
```

### What the Script Does

1. Reads `metadata.json` from each book directory
2. Creates a draft record via the InvenioRDM REST API
3. Uploads the PDF and all HOCR files (`include-hocr` flag)
4. Publishes the record
5. The Celery worker then processes HOCR for full-text search indexing
6. Prints a summary report and saves results to `batch_upload_results.json`

### Output Example

```
[1/2] Uploading: 001_تاريخ_نجد
✓ Using custom fields from metadata.json
Creating draft record...
✅ SUCCESS - 001_تاريخ_نجد uploaded in 45.2s

BATCH UPLOAD SUMMARY
Total books: 2 | Successful: 2 | Failed: 0
Total time: 92.5s
```

---

## HOCR File Requirements

HOCR files must conform to the standard format produced by OCR tools (e.g., Tesseract, ABBYY FineReader):

- **Extension:** `.hocr`
- **Naming:** Zero-padded page numbers: `001.hocr`, `002.hocr`, …, `099.hocr`, `100.hocr`
- **Content:** HTML with `ocrx_word` span elements containing `title="bbox x1 y1 x2 y2"` attributes
- **Encoding:** UTF-8

Pages with no recognised text (blank pages, images without OCR) should be omitted — the indexer handles missing pages gracefully.

---

## Post-Ingestion Verification

After uploading, verify the record is fully functional:

```bash
# 1. Check record is published and searchable
curl -k "https://invenio.turath-project.com/api/records?q=YOUR_TITLE" | jq '.hits.total'

# 2. Verify HOCR full-text search works
curl -k "https://invenio.turath-project.com/api/records?q=custom_fields.turath\:fulltext:\"keyword\"" | jq '.hits.total'

# 3. Verify IIIF manifest is generated
curl -k "https://invenio.turath-project.com/api/records/{record_id}/manifest" | jq '.sequences[0].canvases | length'

# 4. Test in-viewer IIIF search
curl "https://invenio.turath-project.com:5001/search/{record_id}?q=keyword" | jq '.hits | length'
```
