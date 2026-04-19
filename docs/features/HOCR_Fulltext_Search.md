# HOCR Full-Text Search

**Deliverable:** P1-3.1 (Foundational) + P2-1.1 (Enhanced)
**Phases:** 1 and 2 (July–December 2025)
**Date:** March 2026
**Status:** Operational

---

## Overview

Turath InvenioRDM implements a two-layer full-text search system for the *Chronicles of Arabia* OCR content:

1. **Record-level full-text search** — powered by a custom OpenSearch field (`turath:fulltext`) that aggregates all OCR text from a book's HOCR files into a single searchable blob. Users can find which *book* contains a phrase.
2. **Within-document search with visual highlighting** — powered by the IIIF Search microservice. Users can search *within* the Mirador viewer and jump directly to the page and bounding box where a word appears.

---

## Architecture

```
Upload: PDF + HOCR files
              │
              ▼
     Celery background task
              │
     fulltext.py: extract_hocr_text()
     ┌─────────────────────────────┐
     │  for each *.hocr file:      │
     │    parse ocrx_word spans    │
     │    extract text             │
     └─────────────────────────────┘
              │
              ▼
  custom_fields.turath:fulltext  ──► OpenSearch (Arabic analyzer)
              │
              ▼
  User searches at /search?q=...
  Results include fulltext snippets with <em> highlights
```

---

## Phase 1: Foundational HOCR Search

### HOCR Indexing Pipeline

When a record is published, `fulltext.py` runs via Celery:

1. Locates the HOCR directory at `{HOCR_MOUNT_BASE}/{parent_id}/hocr/`
2. Reads all `.hocr` files in page order (`001.hocr`, `002.hocr`, …)
3. Parses each file with BeautifulSoup, extracting text from `ocrx_word` spans
4. Concatenates all page text into a single string
5. Stores the result in the `custom_fields.turath:fulltext` OpenSearch field

### Custom Field Configuration

```python
# invenio.cfg
TextCF(
    name="turath:fulltext",
    field_cls=SanitizedUnicode,
    # Not exposed in deposit form UI — system-managed only
)
```

### Basic Search Query

```bash
# Find books containing a phrase
curl -k "https://invenio.turath-project.com/api/records?q=custom_fields.turath\:fulltext:\"تاريخ نجد\""
```

---

## Phase 2: Enhanced HOCR Search

### Arabic Language Analyzer

The `turath:fulltext` field is indexed with a custom OpenSearch Arabic analyzer providing:

- **Stemming:** Arabic morphological reduction (e.g., `الكتاب` → `كتب`)
- **Stop-word removal:** Common Arabic function words filtered out
- **Unicode normalisation:** Handles variant forms of Arabic characters (hamza variants, tatweel, etc.)

This means users can search for root forms and find all morphological variants.

### Enhanced Search UI

The search interface provides two search modes accessible from both the homepage and the search results page:

**Metadata search mode:**
- Searches title, alternative title, publisher, identifier fields
- Applies wildcard matching automatically: `تاريخ` becomes `*تاريخ*`
- Supports Lucene syntax for advanced users (`turath:title:"exact phrase"`)

**Full-text (HOCR) search mode:**
- Explicitly targets `custom_fields.turath:fulltext`
- Uses the Arabic analyzer for stemmed matching
- Returns search result snippets with `<em>` highlights around matched phrases

```javascript
// TurathHeaderSearchBar.js — query construction
const buildFulltextQuery = (value) => {
  return `custom_fields.turath\\:fulltext:${value}`;
};
```

### Search Result Highlighting

Search results display highlighted HOCR snippets when a fulltext match is found:

```jsx
// TurathResultsListItem.js — snippet rendering
const fulltextSnippets = highlight["custom_fields.turath:fulltext"] || [];
// Rendered in a highlighted box below the record title
```

### Faceted Filtering

Users can filter search results by:
- **Resource type** (`turath:resource_type`)
- **Language** (`turath:language`)
- **Date** (publication year ranges)
- **Subject** (`turath:subject`)
- **Script Type**, **Creator**, **Contributor**, **Format**, **Publisher**, **Creator (Arabic)**, **Alternative Title**, **Identifier**

### Adding, Removing, or Reordering Facets

Facets are configured in code — there is no admin UI toggle. All changes require editing `invenio.cfg` in the [`turath-rdm`](https://github.com/AlABarazi/turath-rdm) repository, then redeploying.

**File:** `invenio.cfg` (root of the repo)

There are two sections to edit together:

**1. Define the facet** (in `RDM_FACETS` dict, ~line 1120):
```python
"language": {
    "facet": CFTermsFacet(
        field="turath:language.id.keyword",
        label=_("Language"),
    ),
    "ui": {
        "field": CFTermsFacet.field("turath:language.id.keyword"),
    },
},
```

**2. Enable it in search** (in `RDM_SEARCH["facets"]` list, ~line 1234):
```python
"facets": RDM_SEARCH["facets"] + [
    "script_type",
    "creator",
    "language",      # ← add or remove facet keys here to show/hide in UI
    "format",
    "resource_type",
    "publisher",
    # ...
],
```

**To hide a facet from the search UI:** remove its key from the `RDM_SEARCH["facets"]` list. The facet definition in `RDM_FACETS` can stay — it will simply be inactive.

**To reorder facets:** change the order of keys in the `RDM_SEARCH["facets"]` list.

**To add a new facet:** add a new entry to `RDM_FACETS` (following the pattern above), then add its key to `RDM_SEARCH["facets"]`.

After editing, deploy with:
```bash
git push origin develop
# wait for GitHub Actions build (~10 min), then:
./scripts/deploy.sh web-ui web-api
```

### Search Performance Optimisation

The `TurathSearchOptions` class excludes the large `turath:fulltext` field from `_source` responses, reducing payload size from ~6 MB to ~200 KB for typical result sets:

```python
class ExcludeFulltextSourceParam:
    """Exclude fulltext blob from search result _source to reduce response size."""
```

---

## Query Reference

### Standard API Queries

```bash
# Metadata search (Arabic)
curl -k "https://invenio.turath-project.com/api/records?q=تاريخ"

# Full-text phrase search
curl -k "https://invenio.turath-project.com/api/records?q=custom_fields.turath\:fulltext:\"تاريخ نجد\""

# Full-text word search (Arabic stemmer applied)
curl -k "https://invenio.turath-project.com/api/records?q=custom_fields.turath\:fulltext:تاريخ"

# Filter by language + fulltext
curl -k "https://invenio.turath-project.com/api/records?q=custom_fields.turath\:fulltext:history&f=turath:language:eng"

# Paginated, sorted by best match
curl -k "https://invenio.turath-project.com/api/records?q=تاريخ&sort=bestmatch&size=10&page=2"
```

### Within-Document IIIF Search (Mirador)

For word-level search with bounding boxes, use the IIIF Search Microservice. See [IIIF API](../APIs/iiif.md).

---

## Test Results (Production)

From the System Testing report (P3-3.2):

| Test | Query | Result | Time |
|------|-------|--------|------|
| Arabic metadata search | `q=تاريخ` | 29 hits | 0.88s |
| HOCR phrase search | `q=...fulltext:"تاريخ نجد"` | 14 hits | 4.43s |
| HOCR broad word search | `q=...fulltext:تاريخ` | 29 hits | 5.75s |
| Pagination | `sort=bestmatch&size=2&page=2` | Distinct pages | — |
| Malformed query | Unclosed quote | HTTP 400 | — |

All tests passed. See the full [Search Robustness Test Report](../testing/Search_Robustness_Test_Report.md).

---

## Backfill

A `backfill_fulltext.py` script is available to re-index HOCR content for existing records without triggering a full re-upload:

```bash
.venv/bin/python scripts/backfill_fulltext.py --base-url https://invenio.turath-project.com
```
