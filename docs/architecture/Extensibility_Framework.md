# InvenioRDM Extensibility Framework

**Deliverable:** P2-4.1 — Extensibility Documentation
**Date:** October 26, 2025
**Subject:** Documenting the flexibility of the metadata and search frameworks for future Turath initiatives.

## Overview
A core requirement for the Turath project is ensuring the platform can adapt to future data modeling needs without requiring a ground-up rewrite. InvenioRDM is built on a highly extensible architecture that allows developers to add custom metadata fields, modify how data is indexed in OpenSearch, and customize the React-based frontend search UI.

This document details how extensibility has been leveraged in the Turath project (specifically for the HOCR full-text search feature) and serves as a guide for future extensions.

---

## 1. Metadata Extensibility (Custom Fields)

InvenioRDM provides a formal "Custom Fields" framework to add domain-specific metadata without hacking the core JSON schemas.

### How it is configured
Custom fields are defined in `invenio.cfg`. They are grouped under a namespace (e.g., `turath`).

```python
# site/turath_inveniordm/config.py or invenio.cfg

from invenio_records_resources.services.custom_fields import TextCF

RDM_CUSTOM_FIELDS = [
    TextCF(name="turath:fulltext")
]

# This tells the frontend UI to expose these fields (if we want them user-editable)
RDM_CUSTOM_FIELDS_UI = [{
    "section": "Turath Data",
    "fields": [
        dict(
            field="turath:fulltext",
            ui_widget="TextArea",
            props=dict(
                label="Extracted OCR Text",
                placeholder="Full text of the document...",
                icon="file text",
                description="Aggregated text from HOCR files for search indexing."
            )
        )
    ]
}]
```

### Applying Custom Fields
After defining custom fields in configuration, they must be initialized in the database and OpenSearch mappings:

```bash
# This updates the OpenSearch mapping and DB tables
pipenv run invenio rdm-records custom-fields init
```

### Future Initiatives
To add new metadata in the future (e.g., "Manuscript Scribe", "Original Calligraphy Style"):
1. Add a new `TextCF` or `KeywordCF` to `RDM_CUSTOM_FIELDS`.
2. Update `RDM_CUSTOM_FIELDS_UI` if you want it visible on the upload form.
3. Run `invenio rdm-records custom-fields init`.
4. Update your ingestion scripts (`upload_book.py`) to pass data into `custom_fields["new_namespace:new_field"]`.

---

## 2. Search & Indexing Extensibility (OpenSearch)

By default, OpenSearch maps text fields for standard keyword matching. However, for features like Arabic full-text search, we need custom analyzers.

### How it is configured
We override the default OpenSearch mappings to tell it *how* to index our custom fields. This is done in the `search/v7/records/` directory.

```json
// site/turath_inveniordm/search/v7/records/custom_fields/turath-fulltext.json
{
  "mappings": {
    "properties": {
      "custom_fields": {
        "properties": {
          "turath:fulltext": {
            "type": "text",
            "analyzer": "arabic",
            "term_vector": "with_positions_offsets"
          }
        }
      }
    }
  }
}
```
*Note: Using `"analyzer": "arabic"` ensures that root-word stemming and stop-word removal specific to the Arabic language are applied to the OCR text.*

### Future Initiatives
If you add a new custom field (e.g., `turath:scribe_name`) and want it to be an exact-match facet filter rather than free-text searchable:
1. Create `search/v7/records/custom_fields/turath-scribe_name.json`.
2. Define its type as `"keyword"`.
3. Rebuild the indices: `invenio rdm-records rebuild-all-indices`.

---

## 3. Frontend UI Extensibility (Overridable Registry)

InvenioRDM's frontend search interface is built with React. To change how search results are displayed or how the search bar behaves, Turath uses InvenioRDM's **Overridable Registry** — a React component substitution system built into InvenioRDM's core.

### How it works

Every UI component in InvenioRDM is registered under a unique string key (e.g., `"InvenioAppRdm.Search.SearchBar.element"`). To replace a component, you export a mapping of those keys to your custom React components, and tell Webpack to load your mapping instead of the default one.

### Step 1 — Write your custom component

```js
// site/turath_inveniordm/assets/semantic-ui/js/turath_inveniordm/search/TurathSearchBar.js

import React from "react";

export function TurathSearchBar({ queryString, onInputChange, executeSearch }) {
  // Custom search bar — adds HOCR fulltext prefix, renders dual-mode UI
  return (
    <input
      value={queryString}
      onChange={(e) => onInputChange(e.target.value)}
      onKeyDown={(e) => e.key === "Enter" && executeSearch()}
      placeholder="Search manuscripts..."
    />
  );
}
```

### Step 2 — Register your override in the mapping file

```js
// site/turath_inveniordm/assets/semantic-ui/js/invenio_app_rdm/overridableRegistry/mapping.js

import { TurathSearchBar } from "../../turath_inveniordm/search/TurathSearchBar";
import { TurathResultsListItemCard } from "../../turath_inveniordm/search/TurathResultsListItemCard";

export const overriddenComponents = {
  "InvenioAppRdm.Search.SearchBar.element": TurathSearchBar,
  "InvenioAppRdm.Search.ResultsList.item": TurathResultsListItemCard,
};
```

### Step 3 — Point Webpack at your mapping file

```python
# site/turath_inveniordm/webpack.py

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "turath-mirador-init": "./js/mirador_init.js",
                "turath-base-theme-rdm": "./js/turath_inveniordm/turath_base_theme_rdm.js",
            },
            aliases={
                # Redirect InvenioRDM's default mapping import to our custom file
                "@js/invenio_app_rdm/overridableRegistry/mapping": (
                    "js/invenio_app_rdm/overridableRegistry/mapping.js"
                ),
            },
        ),
    },
)
```

The webpack alias intercepts the core InvenioRDM bundle's import of its own registry mapping and substitutes your file. This is the **only** Webpack alias needed — all component overrides are expressed as data in `mapping.js`, not as additional aliases.

### Components overridden in Turath

| Registry Key | Custom Component | Purpose |
|---|---|---|
| `InvenioAppRdm.Search.SearchBar.element` | `TurathSearchBar` | Dual-mode search (metadata + HOCR fulltext) with Arabic placeholder |
| `InvenioAppRdm.Search.ResultsList.item` | `TurathResultsListItemCard` | Card layout with HOCR snippet highlighting and IIIF viewer link |

### Future Initiatives

To override any other part of the UI:
1. Find the component's registry key — browse `invenio-app-rdm` source or search for `overrideId` strings in the npm package
2. Write your custom React component
3. Add `"TheKey": YourComponent` to `mapping.js`
4. Run `invenio-cli assets build` — no changes to `webpack.py` needed

**Examples of commonly overridable keys:**
- `InvenioAppRdm.Search.ActiveFilters.element` — customise active filter chips
- `InvenioAppRdm.RecordLandingPage.RecordTitle.container` — override record title display
- `InvenioAppRdm.Search.FacetList.element` — add or reorder sidebar facets

---

## Conclusion
The combination of `invenio.cfg` for data modeling, OpenSearch JSON mappings for index tuning, and the Overridable Registry for UI customization provides a robust, future-proof framework. Turath can easily expand to ingest new data types (like structured prosopography data or geographic coordinates) and surface them in a custom UI — without forking or patching the underlying InvenioRDM engine.
