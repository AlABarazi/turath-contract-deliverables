# Cantaloupe Integration Review & Initial Optimization
**Deliverable Code:** P1-3.1  
**Date:** September 2025  
**Status:** Complete

---

## 1. Executive Summary

This report details the review and initial optimization of the Cantaloupe IIIF Image Server integration within the Turath InvenioRDM platform. The review focused on stability, performance bottlenecks, and configuration efficacy.

**Key Findings:**
1. **Bottleneck Identification:** The primary performance bottleneck was identified as network transfer latency (downloading large PDFs from InvenioRDM to Cantaloupe) rather than image processing speed.
2. **Configuration Cleanup:** extensive testing revealed that many standard tuning parameters (DPI, compression quality) had negligible impact on the specific "time-to-first-byte" issue.
3. **Critical Optimization:** Enabling persistent `FilesystemCache` for derivative images was the single most effective configuration change, reducing load times for cached pages from 3-5 seconds to <0.5 seconds.

---

## 2. Current Integration Status

### Architecture
The system uses **Cantaloupe 5.0.5** running in a Docker container, integrated via a shared filesystem architecture to bypass HTTP overheads where possible.

- **Source:** `FilesystemSource` (Mapped to Docker volume)
- **Integration:** InvenioRDM acts as a proxy/auth layer, forwarding authorized requests to Cantaloupe.
- **Storage:** PDFs are mirrored to a shared volume (`/cantaloupe-files`) accessible by the image server.

### Stability
The integration is stable. The "Self-DoS" deadlock issue observed in earlier development phases (where the application waited for itself via HTTP) was resolved by moving to `FilesystemSource`.

---

## 3. Optimization Review & Implementation

A comprehensive audit of Cantaloupe settings was conducted to improve the "Centre of Arts (CoA)" image display performance.

### 3.1 Settings Audit (What Didn't Work)
We tested several standard optimization parameters which proved ineffective for our specific bottleneck:

- **`PdfBoxProcessor.dpi`**: Adjusting DPI settings (72 vs 150 vs 300) was ignored by the processor or yielded no perceptible speed improvement.
- **`processor.jpg.quality`**: Reducing quality (e.g., to 70) reduced file size but did not improve the initial processing latency.
- **`cache.server.source`**: Intended to cache the source PDF, but found to be unreliable with the current `FilesystemSource` configuration (PDFs were often re-read).

### 3.2 Implemented Optimizations (What Worked)
The following configurations have been applied to the production environment:

#### ✅ 1. Derivative Cache (CRITICAL)
We enabled the `FilesystemCache` for derivative images (tiles). This is the most significant performance driver.

```properties
cache.server.derivative.enabled = true
cache.server.derivative = FilesystemCache
cache.server.derivative.ttl_seconds = 2592000  # 30 Days
FilesystemCache.pathname = /var/cache/cantaloupe
```

**Impact:** 
- **First View:** ~3-5 seconds (Processing overhead)
- **Subsequent Views:** <0.5 seconds (Served from cache)

#### ✅ 2. Configuration Streamlining
We removed ~30 lines of ineffective configuration ("voodoo tuning") to simplify maintenance and reduce the risk of conflicting settings. The configuration now focuses strictly on:
- Source delegation (`FilesystemSource`)
- Derivative caching
- Logging/Error handling

## 5. Conclusion

The Cantaloupe integration is now stable and optimized for repeated access. The implementation of `FilesystemCache` ensures excellent performance for active content. The remaining latency for new content is understood and will be addressed via the Pre-warming strategy in the next phase.
