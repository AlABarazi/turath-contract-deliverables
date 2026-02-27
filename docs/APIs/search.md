# Search API

This document details the REST API endpoints for searching metadata records and performing full-text IIIF searches in Turath InvenioRDM.

## 1. Standard Metadata Search (InvenioRDM)

The main application (port 5000) provides a robust search API backed by OpenSearch.

**Endpoint:** `GET /api/records`

### Querying

You can use the `q` parameter to pass standard OpenSearch/Lucene query string syntax.

```bash
# Search for a specific title
curl -k -sSL "https://invenio.turath-project.com/api/records?q=title:\"Sample Arabic History Book\"" | jq .

# Search for a specific author
curl -k -sSL "https://invenio.turath-project.com/api/records?q=metadata.creators.person_or_org.family_name:Al-Author" | jq .
```

### Full-Text HOCR Search (Custom Field)

Turath InvenioRDM implements a custom field `custom_fields.turath:fulltext` that aggregates all text extracted from a record's HOCR files. This allows searching across the entire text of a book.

**Important:** Because the field name contains a colon (`:`), it must be escaped with a backslash (`\`) in the query string.

```bash
# Search within the full text of the books
# URL-encoded query: q=custom_fields.turath\:fulltext:"specific word"
curl -k -sSL "https://invenio.turath-project.com/api/records?q=custom_fields.turath\:fulltext:\"history\"" | jq .
```

### Pagination and Sorting

- `size`: Number of results per page (default: 10)
- `page`: Page number (default: 1)
- `sort`: Sort field (e.g., `bestmatch`, `newest`)

```bash
curl -k -sSL "https://invenio.turath-project.com/api/records?q=history&sort=bestmatch&size=5&page=2" | jq .
```

---

## 2. IIIF Search Services (Custom Port 5001)

Turath implements the [IIIF Content Search API 1.0](https://iiif.io/api/search/1.0/) via a dedicated lightweight Flask microservice running on port 5001. This service provides search within a specific manifest (record) for the Mirador viewer.

**Base URL for IIIF Search:** `https://invenio.turath-project.com:5001`

### Search within a Record

Returns an AnnotationList of search hits (bounding boxes for words).

**Endpoint:** `GET /search/{record_pid}`

**Parameters:**
- `q`: The query string

```bash
# Search for "the" inside record 7cxkj-kvp29
curl -k -sSL "https://invenio.turath-project.com:5001/search/7cxkj-kvp29?q=the" | jq .
```

### Autocomplete

Provides search term suggestions within a specific record.

**Endpoint:** `GET /autocomplete/{record_pid}`

**Parameters:**
- `q`: The partial query string

```bash
# Get autocomplete suggestions starting with "th"
curl -k -sSL "https://invenio.turath-project.com:5001/autocomplete/7cxkj-kvp29?q=th" | jq .
```

### Page Annotations (Text Overlay)

Returns the full text of a specific page as an AnnotationList, used by Mirador plugins (like text overlay) to render text on top of the image canvas.

**Endpoint:** `GET /annotations/{record_pid}/{page_id}`

- `page_id` is typically formatted as `p001`, `p002`, etc.

```bash
# Get annotations for page 1
curl -k -sSL "https://invenio.turath-project.com:5001/annotations/7cxkj-kvp29/p001" | jq .
```

## Notes
- The IIIF search service automatically resolves the `record_pid` to the underlying `parent_id` to locate the correct HOCR files on the filesystem (`HOCR_MOUNT_BASE`), ensuring search works seamlessly across record versions.
