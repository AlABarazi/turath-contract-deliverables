# Records API

This document details the REST API endpoints for managing metadata records in Turath InvenioRDM.

**Base URL:** `https://127.0.0.1:5000` (or `https://invenio.turath-project.com` in production)

## 1. Get Record by PID

Retrieves the metadata for a specific published record.

**Endpoint:** `GET /api/records/{record_pid}`

```bash
# Basic get (public record)
curl -k -sSL "https://127.0.0.1:5000/api/records/7cxkj-kvp29" | jq .

# With authentication (if restricted)
curl -k -H "Authorization: Bearer $RDM_API_TOKEN" "https://127.0.0.1:5000/api/records/7cxkj-kvp29" | jq .
```

## 2. List Records

Retrieves a paginated list of published records.

**Endpoint:** `GET /api/records`

```bash
# Get the first record
curl -k "https://127.0.0.1:5000/api/records?size=1" | jq .
```

*Note: For querying and searching records, see [search.md](./search.md).*

## 3. Create a Draft Record

To ingest a new record, you must first create a draft.

**Endpoint:** `POST /api/records`

```bash
curl -k -X POST -H "Authorization: Bearer $RDM_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d @metadata.json \
     "https://127.0.0.1:5000/api/records"
```

### Example Metadata Payload (`metadata.json`)
```json
{
  "access": {
    "record": "public",
    "files": "public"
  },
  "files": {
    "enabled": true
  },
  "metadata": {
    "title": "Sample Arabic History Book",
    "resource_type": { "id": "book" },
    "publication_date": "2023",
    "creators": [
      {
        "person_or_org": {
          "type": "personal",
          "family_name": "Al-Author",
          "given_name": "Ahmed"
        }
      }
    ],
    "languages": [{"id": "ara"}]
  }
}
```

## 4. Publish a Draft

Once a draft is created and files are uploaded (see [files.md](./files.md)), you can publish it to make it a formal record.

**Endpoint:** `POST /api/records/{draft_pid}/draft/actions/publish`

```bash
curl -k -X POST -H "Authorization: Bearer $RDM_API_TOKEN" \
     "https://127.0.0.1:5000/api/records/10zkp-d5z36/draft/actions/publish"
```

## 5. Record Structure (Key Fields)

When retrieving a record, pay attention to these structural elements:

```json
{
  "id": "er0yr-89563",
  "is_deleted": false,
  "versions": {
    "is_latest": true,
    "index": 1
  },
  "parent": {
    "id": "0kg1x-s1p14"
  },
  "files": {
    "enabled": true,
    "entries": {
      "001.hocr": { "size": 4879 },
      "document.pdf": { "size": 93520 }
    }
  },
  "links": {
    "self_iiif_manifest": "https://127.0.0.1:5000/api/iiif/record:er0yr-89563/manifest"
  }
}
```

## Notes
- `parent.id` is crucial in Turath for versioning. The filesystem structure for HOCR and Cantaloupe files relies on the `parent.id` to ensure URLs remain stable across record versions.
- SSL uses a self-signed certificate locally; use the `-k` flag with `curl`.
- Use the system identity for internal programmatic access (no token needed internally).
