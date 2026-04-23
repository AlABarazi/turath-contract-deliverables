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

## Pathway 2: Batch Upload Script

For ingesting books with full-text search support, the `records_crud.py` script provides an automated pipeline that handles everything: record creation, file upload, publishing, and search indexing.

### Prerequisites

- **Python 3.9 or later** installed on your computer
  - Mac: open Terminal and run `python3 --version` to check
  - If not installed: download from [python.org](https://www.python.org/downloads/)
- **`requests` library** — install once by running: `pip3 install requests`
- An internet connection to reach `invenio.turath-project.com`

### Step 1 — Create an API Token

The script authenticates to the server using a secret token you generate from your account.

1. Open a browser and go to `https://invenio.turath-project.com/login/`
2. Log in with the admin account
3. Go to: `https://invenio.turath-project.com/account/settings/applications/`
4. Under **Personal access tokens**, click **New token**
5. Give it any name (e.g. `ingestion`) and click **Create**
6. Copy the token immediately — it is only shown once
7. Keep this token; you will use it in the command below

### Step 2 — Prepare the Book Folder

Each book must be in its own folder with this exact structure:

```
070_مجمع_في_التاريخ_النجدي/
├── 070_مجمع_في_التاريخ_النجدي.pdf    ← the scanned book PDF
├── metadata.json                       ← book metadata
├── thumbnail.jpg                       ← cover image shown in search results
└── hocr/
    ├── 001.hocr                        ← OCR text for page 1
    ├── 002.hocr                        ← OCR text for page 2
    └── ...                             ← one file per page
```

**Rules:**
- The folder name and the PDF filename must match exactly
- HOCR files must be zero-padded: `001.hocr`, `002.hocr`, ..., `099.hocr`, `100.hocr`
- `metadata.json` must contain the book's title, author, language, and other fields — see [CoA Metadata Schema](../features/CoA_Metadata_Schema.md) for the full list

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

### Step 3 — Download the Script

Download `records_crud.py` from:

`https://github.com/AlABarazi/turath-rdm/blob/main/scripts/records_crud.py`

Save it to any folder on your computer and note the full path.

### Step 4 — Open Terminal

- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter
- **Windows:** press `Win + R`, type `cmd`, press Enter

Navigate to the folder where you saved the script:

```bash
cd /path/to/folder/where/you/saved/the/script
```

### Step 5 — Run the Command

```bash
RDM_API_TOKEN=<your-token-from-step-1> \
python3 records_crud.py ingest-book \
  --base-url https://invenio.turath-project.com \
  --books-root /path/to/folder/containing/book/folders \
  --book-id "070_مجمع_في_التاريخ_النجدي" \
  --include-hocr
```

**What each part means:**

| Part | Explanation |
|---|---|
| `RDM_API_TOKEN=<your-token>` | The secret token from Step 1. Replace `<your-token>` with the actual token. This authenticates you with the server. |
| `python3 records_crud.py` | Runs the ingestion script using Python 3 |
| `ingest-book` | The operation to perform — creates a new record, uploads all files, publishes the book, and triggers full-text search indexing |
| `--base-url https://invenio.turath-project.com` | The address of the production server — do not change this |
| `--books-root /path/to/books` | The folder on your computer that contains your book folders. If your book is at `/Users/yourname/books/070_.../`, then `--books-root` is `/Users/yourname/books/` |
| `--book-id "070_مجمع_في_التاريخ_النجدي"` | The name of the book folder to upload — must match the folder name exactly, including Arabic characters |
| `--include-hocr` | Uploads the HOCR OCR files. **Required** to make the book full-text searchable in Arabic. Without this flag the book will be published but keyword search inside its pages will not work. |

### What the Script Does (automatically)

1. Reads `metadata.json` from the book directory
2. Creates a draft record via the InvenioRDM REST API
3. Uploads the PDF and thumbnail
4. Uploads all HOCR files from the `hocr/` subfolder (one API call per file — this is the slow part)
5. Publishes the record — makes it publicly visible
6. Triggers full-text indexing — the server processes all HOCR files and makes every word in the book searchable

### Expected Output

You will see progress printed in the terminal as the script runs:

```
✓ Loaded 12 custom fields from metadata.json
[Draft] Created record: abc12-xyz99
[PDF] Uploading 070_مجمع_في_التاريخ_النجدي.pdf ...
[Thumbnail] Uploading thumbnail.jpg ...
[HOCR] Uploading 001.hocr (1/214) ...
[HOCR] Uploading 002.hocr (2/214) ...
...
[HOCR] Uploading 214.hocr (214/214) ...
[Publish] Publishing record ...
[Indexer] Triggering fulltext indexing for abc12-xyz99 ...
[Indexer] ✅ Fulltext indexed successfully
[Indexer]    HOCR files: 214
[Indexer]    Fulltext length: 482300 chars
```

**How long it takes:** depends on your internet connection. Uploading 214 HOCR files typically takes 5–15 minutes. Do not close the terminal while it is running.

### Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Token is wrong or expired | Generate a new token in Step 1 |
| `Book directory not found` | `--books-root` or `--book-id` path is wrong | Check the folder path and name match exactly |
| `No PDF found` | PDF filename does not match folder name | Rename the PDF to match the folder name exactly |
| Script runs but book is not searchable | `--include-hocr` was omitted | Re-run the command with `--include-hocr` |
| Upload stops halfway | Network interruption | Re-run the full command — it will create a new draft |

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
curl -k "https://invenio.turath-project.com/api/iiif/record:{record_id}/manifest" | jq '.sequences[0].canvases | length'

# 4. Test in-viewer IIIF search
curl "https://invenio.turath-project.com:5001/search/{record_id}?q=keyword" | jq '.hits | length'
```
