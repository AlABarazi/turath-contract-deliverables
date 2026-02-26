# Turath APIs

Purpose: Developer-oriented reference for Turath InvenioRDM API Documentation

## Overview
This directory contains API documentation for the Turath InvenioRDM system, including the enhanced IIIF Search services integration.

**Base URL**: `https://127.0.0.1:5000`  
**SSL Note**: Uses self-signed certificates, add `-k` flag to curl commands

## Quick Links

- [Authentication](./auth.md) - API token authentication
- [Records](./records.md) - Record management endpoints
- [IIIF](./iiif.md) - IIIF Presentation API with Search services
- [Files](./files.md) - File upload and download
- [Search](./search.md) - Search API endpoints
- [Vocabularies](./vocabularies.md) - Controlled vocabularies

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
      "@id": "https://127.0.0.1:5001/search/{record_pid}",
      "profile": "http://iiif.io/api/search/0/search",
      "label": "Search within this manifest"
    }
  ]
}
```

## Configuration
- **IIIF Search Enabled**: `RDM_IIIF_SEARCH_ENABLED = True`
- **Search Service Base URL**: `https://127.0.0.1:5001`
## Quick Start (verified examples)
- Get IIIF Manifest for record `7cxkj-kvp29`:
```bash
curl -k -sSL "https://127.0.0.1:5000/api/iiif/record:7cxkj-kvp29/manifest" | jq .
```
- Get record by PID:
```bash
curl -k -sSL "https://127.0.0.1:5000/api/records/7cxkj-kvp29" | jq .
```
