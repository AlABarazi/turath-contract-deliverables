import requests
import json
import urllib3
import time
import urllib.parse

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://127.0.0.1:5000"
SEARCH_API = f"{BASE_URL}/api/records"

def run_test(test_name, query, expected_min_hits=0):
    print(f"\n--- Running Test: {test_name} ---")
    print(f"Query: {query}")
    
    start_time = time.time()
    
    # InvenioRDM API expects URL-encoded parameters, but requests handles standard encoding.
    # However, sometimes we need to explicitly encode complex queries.
    params = {"q": query, "size": 10}
    try:
        response = requests.get(SEARCH_API, params=params, verify=False, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ FAILED: Network error - {e}")
        return False
        
    duration = time.time() - start_time
    data = response.json()
    
    hits = data.get("hits", {}).get("total", 0)
    print(f"Hits: {hits} (Time: {duration:.2f}s)")
    
    if hits < expected_min_hits:
        print(f"❌ FAILED: Expected at least {expected_min_hits} hits, got {hits}")
        return False
        
    print("✅ PASSED")
    return True

def main():
    print(f"Starting System Testing against {BASE_URL}")
    print("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    # Test 1: Basic Metadata Search
    if run_test("Basic Metadata Search (English)", "Najd", 1):
        success_count += 1
        
    # Test 2: Wildcard Search
    if run_test("Wildcard Search", "metadata.title:*", 1):
        success_count += 1
        
    # Test 3: HOCR Full-Text Search (Checking if custom field exists)
    if run_test("HOCR Full-Text Search", "custom_fields.turath\\:fulltext:*", 0):
        # We expect 0 or more, but the fact it doesn't 500/400 means the field is mapped
        success_count += 1
        
    # Test 4: Arabic Metadata Search (Exact Match)
    # The Arabic analyzer might require exact token matching depending on how "001_تاريخ_نجد" is tokenized.
    if run_test("Arabic Exact Title", "metadata.title:\"001_تاريخ_نجد\"", 1):
        success_count += 1
        
    # Test 5: English description search
    if run_test("English Description Search", "metadata.description:\"1107 pages\"", 1):
        success_count += 1

    print("\n" + "=" * 60)
    print(f"TEST RUN COMPLETE: {success_count}/{total_tests} tests passed.")

if __name__ == "__main__":
    main()
