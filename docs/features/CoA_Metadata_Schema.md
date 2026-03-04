# Chronicles of Arabia (CoA) Metadata Schema

**Deliverable:** P1-2.1 — Functioning deposit form for CoA; Documented flexible metadata schema
**Phase:** 1 (July–September 2025)
**Date:** March 2026
**Status:** Implemented and operational

---

## Overview

The Turath InvenioRDM instance extends the standard InvenioRDM data model with a **custom metadata schema** specifically designed for the *Chronicles of Arabia* (CoA) collection. The schema is implemented using InvenioRDM's Custom Fields framework under the `turath:` namespace, making it fully independent from the base data model and easily extensible to other collections.

All fields are exposed in the web deposit form via `RDM_CUSTOM_FIELDS_UI` and indexed in OpenSearch for filtering, faceting, and full-text search.

---

## Schema Design Principles

- **Namespace isolation:** All fields use the `turath:` prefix, preventing conflicts with InvenioRDM core fields
- **Search-first design:** Key string fields use `use_as_filter=True`, ensuring they are indexed as keywords for faceted search
- **Controlled vocabularies:** Authority lists (`creators`, `subjects`, `languages`, etc.) are managed as InvenioRDM Vocabulary resources for consistency
- **Arabic language support:** Arabic-script text fields are indexed with a custom Arabic OpenSearch analyzer (stemming + stop-word removal)
- **Multi-value support:** Fields that can have multiple values (creators, subjects, languages) use `multiple=True`

---

## Field Reference

### Title Information

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:title` | Text | No | Primary title. Capitalise first word; preserve original punctuation. |
| `turath:alternative_title` | Text | Yes | Alternative or transliterated titles. Required for Arabic-script titles; use ALA-LC for transliterations. |
| `turath:alternative_title_script` | Vocabulary (`title_scripts`) | No | Script type of the alternative title |

### Creators & Contributors

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:creator` | Vocabulary (`creators`) | Yes | Personal names, groups, or organisations responsible for the intellectual content |
| `turath:creator_arabic` | Keyword | Yes | Creator name in Arabic script |
| `turath:contributor` | Vocabulary (`contributors`) | Yes | Secondary authors, editors, transcribers. Required for oral histories |
| `turath:contributor_arabic` | Keyword | Yes | Contributor name in Arabic script |
| `turath:contributor_type` | Vocabulary (`contributor_types`) | No | Role of the contributor (editor, illustrator, transcriber, etc.) |

### Publication Details

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:publisher` | Keyword | Yes | Organisation or corporate entity responsible for publication |
| `turath:date` | Text (W3CDTF) | No | Date of the resource in ISO 8601 format (YYYY, YYYY-MM, or YYYY-MM-DD) |
| `turath:date_issued` | EDTF Date | No | Date of formal issuance |
| `turath:date_type` | Vocabulary (`date_types`) | No | Type of date (created, modified, issued, etc.) |

### Content Description

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:subject` | Vocabulary (`subjects`) | Yes | Topics covered by the resource |
| `turath:description` | Text (HTML) | Yes | Full description. Include abstract, table of contents, or summary |
| `turath:description_type` | Vocabulary (`description_types`) | No | Type of description (abstract, table of contents, etc.) |

### Classification

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:resource_type` | Vocabulary (`resourcetypes`) | No | General nature or genre of the resource |
| `turath:format` | Vocabulary (`formats`) | Yes | File format or physical medium |
| `turath:format_extent` | Text | No | Size or duration of the resource (e.g., "342 pages") |
| `turath:script_type` | Vocabulary (`script_types`) | No | Script used in the resource (Arabic, Latin, Ottoman Turkish, etc.) |
| `turath:language` | Vocabulary (`languages`) | Yes | Languages used in the resource (ISO 639-2 codes) |

### Identifiers & Relations

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:identifier` | Text | Yes | For digital objects: include filename with extension. Enter in order of importance |
| `turath:source` | Text | Yes | Original source information (pre-digitisation details) |
| `turath:relation_type` | Vocabulary (`relationtypes`) | No | Type of relationship to other resources |
| `turath:relation_identifier` | Text | No | Identifier of the related resource |
| `turath:bibliographic_citation` | Text (HTML) | Yes | Bibliographic reference for the resource |

### Geographic & Temporal Coverage

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:coverage_temporal_start` | Text (W3CDTF) | No | Start date of the time period covered in the content |
| `turath:coverage_temporal_end` | Text (W3CDTF) | No | End date of the time period covered in the content |
| `turath:coverage_spatial` | Vocabulary (`places`) | Yes | Geographic areas covered by the content |
| `turath:geolocation_point` | Text | No | Precise geographic coordinates (decimal degrees) |

### Rights

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:rights` | Vocabulary (`licenses`) | No | Rights and access information |
| `turath:rights_uri` | Text | No | URL to the rights statement |
| `turath:rights_identifier` | Text | No | Standardised rights identifier (e.g., `CC-BY-4.0`) |

### Internal (System-Managed)

| Field | Type | Multiple | Description |
|-------|------|----------|-------------|
| `turath:fulltext` | Text (Arabic-analyzed) | No | Aggregated OCR text from all HOCR files. Populated automatically by the HOCR indexing pipeline. **Not editable via the deposit form.** |

---

## OpenSearch Indexing

Key search fields and their boost values for relevance ranking:

```python
RDM_SEARCH = {
    "query_string": {
        "fields": [
            "custom_fields.turath:title^3",
            "custom_fields.turath:alternative_title^2",
            "custom_fields.turath:publisher.keyword^2",
            "custom_fields.turath:identifier^2",
        ]
    }
}
```

The `turath:fulltext` field uses a dedicated **Arabic text analyzer** configured in OpenSearch with:
- Language-specific stemming (Arabic morphological reduction)
- Stop-word removal
- Unicode normalisation

---

## Deposit Form Structure

The deposit form groups fields into collapsible sections for usability:

1. **Title Information** — title, alternative title, script
2. **Creators & Contributors** — creator, creator (Arabic), contributor, contributor (Arabic), role
3. **Publication Details** — publisher, date, date type
4. **Content Description** — subject, description, description type
5. **Classification** — resource type, format, extent, script type, language
6. **Identifiers & Relations** — identifier, source, relation type, citation
7. **Geographic & Temporal Coverage** — temporal start/end, spatial coverage, coordinates
8. **Rights** — rights, rights URI, rights identifier

---

## Extensibility

To add a new metadata field for a future collection:

```python
# In invenio.cfg — add to RDM_CUSTOM_FIELDS list
TextCF(
    name="turath:new_field",
    field_cls=SanitizedUnicode,
    field_args={"description": "Description of the new field"}
)
```

```python
# In invenio.cfg — add to RDM_CUSTOM_FIELDS_UI list
dict(
    field="turath:new_field",
    ui_widget="Input",
    props=dict(label="New Field", placeholder="Enter value")
)
```

No database migrations are required — InvenioRDM handles custom fields dynamically. See the [Extensibility Framework](../architecture/Extensibility_Framework.md) for full guidance.
