"""
Turath Search Robustness Test Suite
=====================================
Deliverable: P3-3.2

Validates all search capabilities of the Turath InvenioRDM platform:
  - Standard metadata search (English and Arabic)
  - HOCR full-text search (phrase and stemmed)
  - Custom field search (turath: namespace fields)
  - Faceted / filtered search
  - IIIF Content Search API (in-document search microservice)
  - Pagination and sorting
  - Malformed query error handling

Usage:
    python run_search_tests.py --target local    # default
    python run_search_tests.py --target prod
"""

import requests
import json
import urllib3
import time
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

passed = 0
failed = 0


def result(ok, name, detail=""):
    global passed, failed
    status = "✅ PASSED" if ok else "❌ FAILED"
    print(f"  {status}: {name}")
    if detail:
        print(f"         {detail}")
    if ok:
        passed += 1
    else:
        failed += 1
    return ok


def search(base_url, q, **kwargs):
    params = {"q": q, "size": kwargs.get("size", 10)}
    if "page" in kwargs:
        params["page"] = kwargs["page"]
    if "sort" in kwargs:
        params["sort"] = kwargs["sort"]
    if "f" in kwargs:
        params["f"] = kwargs["f"]
    start = time.time()
    resp = requests.get(f"{base_url}/api/records", params=params, verify=False, timeout=15)
    elapsed = time.time() - start
    resp.raise_for_status()
    data = resp.json()
    total = data.get("hits", {}).get("total", 0)
    if isinstance(total, dict):
        total = total.get("value", 0)
    return total, data.get("hits", {}).get("hits", []), elapsed


def run_tests(base_url, iiif_url):
    print(f"\n{'='*65}")
    print(f"Turath Search Robustness Tests — {base_url}")
    print(f"{'='*65}\n")

    # ── Group 1: Metadata Search ────────────────────────────────────
    print("[ Group 1: Standard Metadata Search ]")

    try:
        total, hits, t = search(base_url, "001_تاريخ_نجد")
        result(total > 0, "Metadata search — title filename (English)",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "Metadata search — title filename", str(e))

    try:
        total, hits, t = search(base_url, "تاريخ")
        result(total > 0, "Metadata search — Arabic word",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "Metadata search — Arabic word", str(e))

    # ── Group 2: Custom Field Search ────────────────────────────────
    print("\n[ Group 2: Custom Turath Field Search ]")

    try:
        total, _, t = search(base_url, r'custom_fields.turath\:title:تاريخ')
        result(total > 0, "Custom field search — turath:title",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "Custom field search — turath:title", str(e))

    try:
        total, _, t = search(base_url, r'custom_fields.turath\:date:2010')
        result(total >= 0, "Custom field search — turath:date",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "Custom field search — turath:date", str(e))

    # ── Group 3: HOCR Full-Text Search ──────────────────────────────
    print("\n[ Group 3: HOCR Full-Text Search ]")

    try:
        total, _, t = search(base_url, r'custom_fields.turath\:fulltext:"تاريخ نجد"')
        result(total > 0, "HOCR fulltext — exact Arabic phrase",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "HOCR fulltext — exact phrase", str(e))

    try:
        total, _, t = search(base_url, r'custom_fields.turath\:fulltext:تاريخ')
        result(total > 0, "HOCR fulltext — broad Arabic word (stemmed)",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "HOCR fulltext — broad word", str(e))

    # ── Group 4: Faceted / Filtered Search ──────────────────────────
    print("\n[ Group 4: Faceted Search ]")

    try:
        total, _, t = search(base_url, "تاريخ", f="resource_type:publication-book")
        result(total > 0, "Faceted search — filter by resource_type:publication-book",
               f"{total} hits in {t:.2f}s")
    except Exception as e:
        result(False, "Faceted search — resource_type filter", str(e))

    # ── Group 5: IIIF Content Search API ────────────────────────────
    print("\n[ Group 5: IIIF Content Search API (port 5001) ]")

    # First get a valid PID
    try:
        _, hits, _ = search(base_url, r'custom_fields.turath\:fulltext:نجد', size=1)
        if not hits:
            _, hits, _ = search(base_url, "تاريخ", size=1)
        pid = hits[0]["id"] if hits else None
    except Exception:
        pid = None

    if pid:
        try:
            resp = requests.get(f"{iiif_url}/search/{pid}?q=%D9%86%D8%AC%D8%AF",
                                verify=False, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            iiif_hits = data.get("hits", [])
            resources = data.get("resources", [])
            result(len(iiif_hits) > 0, "IIIF search — in-document search for 'نجد'",
                   f"{len(iiif_hits)} hits, {len(resources)} annotations with bounding boxes")
        except Exception as e:
            result(False, "IIIF search — in-document search", str(e))

        try:
            resp = requests.get(f"{iiif_url}/autocomplete/{pid}?q=%D9%86%D8%AC",
                                verify=False, timeout=15)
            resp.raise_for_status()
            terms = resp.json().get("terms", [])
            result(len(terms) > 0, "IIIF autocomplete — prefix 'نج'",
                   f"Suggestions: {[t['match'] for t in terms[:5]]}")
        except Exception as e:
            result(False, "IIIF autocomplete", str(e))

        try:
            resp = requests.get(f"{iiif_url}/annotations/{pid}/p001",
                                verify=False, timeout=15)
            resp.raise_for_status()
            words = resp.json().get("resources", [])
            result(len(words) > 0, "IIIF annotations — text overlay words on p001",
                   f"{len(words)} words with xywh bounding boxes")
        except Exception as e:
            result(False, "IIIF annotations — text overlay", str(e))
    else:
        result(False, "IIIF tests skipped", "No records found to test against")

    # ── Group 6: Pagination & Sorting ───────────────────────────────
    print("\n[ Group 6: Pagination & Sorting ]")

    try:
        _, p1_hits, _ = search(base_url, "تاريخ", size=2, page=1, sort="bestmatch")
        _, p2_hits, _ = search(base_url, "تاريخ", size=2, page=2, sort="bestmatch")
        p1_ids = {h["id"] for h in p1_hits}
        p2_ids = {h["id"] for h in p2_hits}
        overlap = p1_ids & p2_ids
        result(not overlap and len(p1_ids) > 0,
               "Pagination — pages 1 and 2 return distinct records",
               f"Page 1: {list(p1_ids)} | Page 2: {list(p2_ids)}")
    except Exception as e:
        result(False, "Pagination test", str(e))

    # ── Group 7: Error Handling ──────────────────────────────────────
    print("\n[ Group 7: Error Handling ]")

    try:
        resp = requests.get(f"{base_url}/api/records",
                            params={"q": 'custom_fields.turath:fulltext:"unclosed quote'},
                            verify=False, timeout=15)
        result(resp.status_code == 400,
               "Malformed Lucene query returns HTTP 400",
               f"Got HTTP {resp.status_code}")
    except Exception as e:
        result(False, "Error handling test", str(e))

    # ── Summary ──────────────────────────────────────────────────────
    total_tests = passed + failed
    print(f"\n{'='*65}")
    print(f"Results: {passed}/{total_tests} tests passed")
    if failed > 0:
        print(f"⚠️  {failed} test(s) failed — check environment and test data.")
    else:
        print("✅ All tests passed.")
    print(f"{'='*65}\n")


def main():
    parser = argparse.ArgumentParser(description="Turath Search Robustness Tests")
    parser.add_argument("--target", choices=["local", "prod"], default="local")
    args = parser.parse_args()

    if args.target == "prod":
        base_url = "https://invenio.turath-project.com"
        iiif_url = "https://invenio.turath-project.com:5001"
    else:
        base_url = "https://127.0.0.1:5000"
        iiif_url = "https://127.0.0.1:5001"

    run_tests(base_url, iiif_url)


if __name__ == "__main__":
    main()
