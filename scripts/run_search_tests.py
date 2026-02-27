import requests
import json
import urllib3
import time
import argparse
import sys

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_test(base_url, test_name, query, expected_min_hits=0):
    search_api = f"{base_url}/api/records"
    print(f"\n--- Running Test: {test_name} ---")
    print(f"Query: {query}")
    
    start_time = time.time()
    params = {"q": query, "size": 10}
    try:
        response = requests.get(search_api, params=params, verify=False, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ FAILED: Network error or bad response - {e}")
        return False
        
    duration = time.time() - start_time
    data = response.json()
    
    # Handle different OpenSearch version responses
    hits_obj = data.get("hits", {}).get("total", 0)
    hits = hits_obj if isinstance(hits_obj, int) else hits_obj.get("value", 0)
    
    print(f"Hits: {hits} (Time: {duration:.2f}s)")
    
    if hits < expected_min_hits:
        print(f"⚠️ WARNING: Expected at least {expected_min_hits} hits, got {hits}.")
        print("   Note: If running against a new environment (like Prod), ensure the test data has been ingested.")
        return False
        
    print("✅ PASSED")
    return True

def run_pagination_test(base_url):
    print("\n--- Running Test: Search Pagination & Sorting ---")
    search_api = f"{base_url}/api/records"
    
    # Page 1
    params_p1 = {"q": "تاريخ", "size": 2, "page": 1, "sort": "bestmatch"}
    print(f"Fetching Page 1 (size=2)...")
    resp1 = requests.get(search_api, params=params_p1, verify=False)
    hits1 = resp1.json().get("hits", {}).get("hits", [])
    
    # Page 2
    params_p2 = {"q": "تاريخ", "size": 2, "page": 2, "sort": "bestmatch"}
    print(f"Fetching Page 2 (size=2)...")
    resp2 = requests.get(search_api, params=params_p2, verify=False)
    hits2 = resp2.json().get("hits", {}).get("hits", [])
    
    if not hits1:
        print("⚠️ WARNING: Not enough records to test pagination.")
        return False
        
    id_p1 = [h.get("id") for h in hits1]
    id_p2 = [h.get("id") for h in hits2]
    
    # Verify records are different
    overlap = set(id_p1).intersection(set(id_p2))
    if overlap:
        print(f"❌ FAILED: Pagination overlap detected! {overlap}")
        return False
        
    print(f"Page 1 IDs: {id_p1}")
    print(f"Page 2 IDs: {id_p2}")
    print("✅ PASSED: Pagination returns distinct results")
    return True

def run_error_handling_test(base_url):
    print("\n--- Running Test: Malformed Query Error Handling ---")
    search_api = f"{base_url}/api/records"
    
    # Intentionally malformed Lucene query (unclosed quote)
    params = {"q": 'custom_fields.turath:fulltext:"unclosed quote'}
    print(f"Query: {params['q']}")
    
    resp = requests.get(search_api, params=params, verify=False)
    
    if resp.status_code == 400:
        print(f"Received expected HTTP 400 Bad Request.")
        print("✅ PASSED: System gracefully handles malformed queries without crashing.")
        return True
    else:
        print(f"❌ FAILED: Expected HTTP 400, got HTTP {resp.status_code}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Search Robustness Tests")
    parser.add_argument("--target", choices=["local", "prod"], default="local", 
                        help="Target environment to test (default: local)")
    args = parser.parse_args()

    if args.target == "prod":
        base_url = "https://invenio.turath-project.com"
    else:
        base_url = "https://127.0.0.1:5000"

    print(f"Starting System Testing against {args.target.upper()} ({base_url})")
    print("=" * 60)
    
    success_count = 0
    total_tests = 6
    
    # Test 1: Basic Metadata Search
    title_query = "Najd" if args.target == "local" else "001_تاريخ_نجد"
    if run_test(base_url, f"Basic Metadata Search ({args.target})", title_query, 1):
        success_count += 1
        
    # Test 2: Arabic Metadata Search
    if run_test(base_url, "Arabic Metadata Search", "تاريخ", 1):
        success_count += 1
        
    # Test 3: HOCR Full-Text Search (Exact Phrase)
    if run_test(base_url, "HOCR Full-Text Search (Exact Phrase)", r'custom_fields.turath\:fulltext:"تاريخ نجد"', 1):
        success_count += 1

    # Test 4: HOCR Full-Text Search (Broad)
    if run_test(base_url, "HOCR Full-Text Search (Broad)", r"custom_fields.turath\:fulltext:تاريخ", 1):
        success_count += 1

    # Test 5: Pagination
    if run_pagination_test(base_url):
        success_count += 1

    # Test 6: Error Handling
    if run_error_handling_test(base_url):
        success_count += 1

    print("\n" + "=" * 60)
    print(f"Test Execution Complete. ({success_count}/{total_tests} executed successfully)")
    print("=" * 60)

if __name__ == "__main__":
    main()
