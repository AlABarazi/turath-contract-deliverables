# Files API

This document details the REST API endpoints for managing files attached to records in Turath InvenioRDM.

## Overview

Files in InvenioRDM are attached to drafts before they are published. The basic workflow for adding a file is:
1. Initialize the file upload.
2. Upload the file content.
3. Commit the file upload.

## 1. Initialize File Upload

Prepares the draft record to receive a specific file.

**Endpoint:** `POST /api/records/{draft_pid}/draft/files`

**Body:**
```json
[
  { "key": "document.pdf" }
]
```

**Example:**
```bash
curl -k -X POST -H "Authorization: Bearer $RDM_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '[{"key": "document.pdf"}]' \
     "https://invenio.turath-project.com/api/records/10zkp-d5z36/draft/files"
```

## 2. Upload File Content

Uploads the actual byte content of the file.

**Endpoint:** `PUT /api/records/{draft_pid}/draft/files/{filename}/content`

**Example:**
```bash
curl -k -X PUT -H "Authorization: Bearer $RDM_API_TOKEN" \
     -H "Content-Type: application/octet-stream" \
     --data-binary @path/to/local/document.pdf \
     "https://invenio.turath-project.com/api/records/10zkp-d5z36/draft/files/document.pdf/content"
```

## 3. Commit File Upload

Finalizes the upload process, telling InvenioRDM the file is fully transferred.

**Endpoint:** `POST /api/records/{draft_pid}/draft/files/{filename}/commit`

**Example:**
```bash
curl -k -X POST -H "Authorization: Bearer $RDM_API_TOKEN" \
     "https://invenio.turath-project.com/api/records/10zkp-d5z36/draft/files/document.pdf/commit"
```

## 4. Download a File

Retrieves the content of an uploaded file from a published record.

**Endpoint:** `GET /api/records/{record_pid}/files/{filename}/content`

**Example:**
```bash
curl -k -sSLO "https://invenio.turath-project.com/api/records/7cxkj-kvp29/files/document.pdf/content"
```

*Note: The `/content` path is crucial. Without it, you get the file's metadata, not the binary content.*

## Notes on File Handling in Turath

In the Turath system, while files are uploaded via these APIs to InvenioRDM's standard storage, there is an asynchronous/scripted process that also mirrors these files (specifically PDFs and HOCRs) to the Cantaloupe/Search service mounts (`cantaloupe-files` and `hocr_mount`).

This is why `parent.id` is critical—the external viewers rely on stable filesystem paths mapped to the parent ID, not the specific version's PID.
