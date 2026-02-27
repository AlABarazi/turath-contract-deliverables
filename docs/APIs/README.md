# Turath APIs

Purpose: Developer-oriented reference for Turath InvenioRDM API Documentation

## Overview
This directory contains API documentation for the Turath InvenioRDM system, including the enhanced IIIF Search services integration.

**Base URL**: `https://invenio.turath-project.com`  

## Quick Links

- [Records API](./records.md) - Record management endpoints
- [Search API](./search.md) - Search API endpoints (including HOCR)
- [Files API](./files.md) - File upload and download workflows
- [RAG Feasibility Report](./RAG_Feasibility_Report.md) - Proof of concept for LLM integration

## Enhanced Features

### IIIF Search Services
Our InvenioRDM instance includes enhanced IIIF manifests with integrated Search and Autocomplete services:

```json
{
  "@context": [
    "http://iiif.io/api/presentation/2/context.json",
    "http://iiif.io/api/search/0/context.json"
  ],
  "service": [
    {
      "@id": "https://invenio.turath-project.com:5001/search/{record_pid}",
      "profile": "http://iiif.io/api/search/0/search",
      "label": "Search within this manifest"
    }
  ]
}
```

## Configuration
- **IIIF Search Enabled**: `RDM_IIIF_SEARCH_ENABLED = True`
- **Search Service Base URL**: `https://invenio.turath-project.com:5001`
## Quick Start (verified examples)
- Get IIIF Manifest for record `7cxkj-kvp29`:
```bash
curl -k -sSL "https://invenio.turath-project.com/api/iiif/record:7cxkj-kvp29/manifest" | jq .
```
- Get record by PID:
```bash
curl -k -sSL "https://invenio.turath-project.com/api/records/7cxkj-kvp29" | jq .
```
