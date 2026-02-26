# InvenioRDM Extensibility Framework

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

## 3. Frontend UI Extensibility (React Overrides)

InvenioRDM's frontend search interface is built with React. To change how search results are displayed or how the search bar behaves, we use **Webpack Alias Overrides**.

### How it is configured
Instead of editing core Invenio files, we create a custom React component and tell Webpack to load *our* file instead of the default one.

```python
# site/turath_inveniordm/webpack.py

"aliases": {
    # Override the default SearchBar component
    "@invenio-app-rdm/components/SearchBar": "components/SearchBar",
},
```

We then place our custom component in `site/turath_inveniordm/assets/semantic-ui/js/turath_inveniordm/components/SearchBar/index.js`. 

In the Turath project, this was used to intercept the user's query and automatically append `custom_fields.turath\:fulltext:` to it, ensuring that simple searches hit our massive OCR text blob seamlessly.

### Future Initiatives
This override mechanism can be used to customize almost any part of the UI:
- **Search Results List:** Override `@invenio-app-rdm/search/components/ResultsList`.
- **Record Landing Page:** Override components in `@invenio-app-rdm/record/`.
- **Facets/Filters:** Add new sidebar filters by overriding the Facets component and linking them to your new `KeywordCF` custom fields.

Always remember to run `invenio-cli assets build` after modifying React components or Webpack aliases.

---

## Conclusion
The combination of `invenio.cfg` for data modeling, OpenSearch JSON mappings for index tuning, and Webpack Aliases for UI customization provides a robust, future-proof framework. Turath can easily expand to ingest new data types (like structured prosopography data or geographic coordinates) without replacing the underlying InvenioRDM engine.
