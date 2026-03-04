# Mirador Viewer with Text Overlay

**Deliverable:** P2-2.1 — Mirador with functional text overlay
**Phase:** 2 (October–November 2025)
**Date:** March 2026
**Status:** Operational

---

## Overview

The Turath Mirador implementation provides two complementary text-access features for scanned manuscripts:

1. **HOCR Text Overlay** — every recognised word from the OCR is rendered as an invisible, selectable, hoverable layer directly over the scanned image, enabling text selection and copy-paste from manuscripts
2. **IIIF In-Viewer Search** — users can type a query in the Mirador search panel; matching words are highlighted with bounding boxes directly on the manuscript page, and results appear as a sidebar list with page navigation

Both features are integrated into a custom Mirador bundle (`mirador.min.js`) that is served as a static file within InvenioRDM.

---

## Text Overlay (textoverlay-mirador Plugin)

### What It Does

The text overlay renders a transparent HTML layer over each canvas (manuscript page) in Mirador. Each `ocrx_word` element from the HOCR file becomes a positioned `<span>` at the exact bounding box coordinates. This enables:

- **Text selection** — users can select and copy Arabic text from scanned pages
- **Hover highlighting** — hovering over words highlights them visually
- **Accessible reading** — screen readers can access the underlying OCR text

### Implementation

The `textoverlay-mirador` plugin is bundled directly into the custom `mirador.min.js`:

```
site/turath_inveniordm/static/mirador/
├── mirador.min.js                  ← current bundle (includes textoverlay)
├── mirador.min.js.withouttextoverlay  ← pre-overlay backup (reference)
├── mirador.min.js.backup           ← incremental backup
└── mirador.min.css
```

The plugin fetches word-level annotations from the IIIF Annotations endpoint:

```
GET https://invenio.turath-project.com:5001/annotations/{record_pid}/{page_id}
```

This returns an `sc:AnnotationList` with one `oa:Annotation` per word, each containing:
- `chars` — the OCR word text
- `on` — canvas URI + `#xywh=x,y,width,height` bounding box

The plugin maps these bounding boxes to CSS `position: absolute` elements on the canvas container.

See [IIIF API — Annotations endpoint](../APIs/iiif.md#3-annotations-text-overlay) for the full response format.

---

## IIIF In-Viewer Search

### What It Does

The Mirador search panel (accessible via the search icon in the window toolbar) allows users to search for a term within the currently open manuscript. Results show:

- A list of matching passages with surrounding context
- A badge showing the page number of each hit
- Clicking a result jumps Mirador to that page and draws bounding box overlays on the matching words

### Architecture

Mirador uses the IIIF Content Search API 1.0, following the service URL embedded in each IIIF manifest:

```json
"service": [{
  "@id": "https://invenio.turath-project.com:5001/search/{record_pid}",
  "profile": "http://iiif.io/api/search/1/search"
}]
```

The search microservice processes the query in parallel across all HOCR pages and returns an `sc:AnnotationList` with:
- `resources` — one annotation per hit (bounding box + matched text)
- `hits` — human-readable results for the sidebar (context before/after the match)

See [IIIF API — Search endpoint](../APIs/iiif.md#1-search-within-a-record) for the full response format.

### Auto-Search from Global Search Results

When a user finds a record via the global HOCR search and clicks through, the Mirador viewer can automatically open with the search query pre-populated. The `hocr_query` URL parameter triggers this:

```
/records/{id}?hocr_query=تاريخ
```

`mirador_init.js` detects this parameter and:
1. Opens the search sidebar panel automatically
2. Populates the Mirador search input with the query
3. Triggers the search, highlighting all matches on the first result page

---

## Mirador Initialization

The viewer is initialised via `mirador_init.js` using a CSP-safe pattern (no inline JavaScript):

```html
<!-- Record detail template -->
<div id="mirador-viewer"
     data-manifest="/api/records/{record_id}/manifest"
     data-config='{"id": "mirador-viewer"}'>
</div>
```

```javascript
// mirador_init.js — reads data attributes, no inline JS
var container = document.getElementById('mirador-viewer');
var manifestUrl = container.getAttribute('data-manifest');
window.Mirador.viewer({
    id: 'mirador-viewer',
    windows: [{ manifestId: manifestUrl }]
});
```

---

## Configuration Reference

| Config key | Location | Description |
|-----------|----------|-------------|
| `IIIF_SEARCH_SERVICE_BASE_URL` | `invenio.cfg` | Base URL of the IIIF Search microservice |
| Content Security Policy `connect-src` | `invenio.cfg` | Must include the search service URL to allow browser fetches |
| `data-manifest` attribute | Record detail template | Passed to Mirador as the manifest URL |

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Viewer | Mirador 3 |
| Text overlay | `textoverlay-mirador` plugin (bundled into `mirador.min.js`) |
| Search protocol | IIIF Content Search API 1.0 |
| Annotations backend | Custom Flask microservice (`services/search_service/app.py`) |
| HOCR storage | AWS EFS (mounted at `/hocr_mount/books/{parent_id}/hocr/`) |
| IIIF Image Server | Cantaloupe (for high-resolution tile delivery) |
