import requests
import json
import urllib3
import argparse
import sys

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_rag_test(base_url, iiif_url):
    print(f"Starting RAG Feasibility Test against {base_url}")
    print("=" * 60)
    
    # 1. Fetch Metadata
    print("\n[Step 1] Fetching Record Metadata...")
    search_api = f"{base_url}/api/records?sort=newest&size=1"
    
    try:
        response = requests.get(search_api, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch records: {e}")
        return
        
    hits = data.get("hits", {}).get("hits", [])
    if not hits:
        print("❌ No published records found. Cannot perform RAG test. Please upload test data.")
        return
        
    record = hits[0]
    pid = record.get("id")
    metadata = record.get("metadata", {})
    
    title = metadata.get("title", "Unknown Title")
    description = metadata.get("description", "No description")
    
    print(f"✅ Found Record: {pid}")
    print(f"   Title: {title}")
    
    # 2. Fetch OCR Data (Simulating a RAG chunk fetch)
    print(f"\n[Step 2] Fetching OCR Data for Page 1 of {pid}...")
    annotations_api = f"{iiif_url}/annotations/{pid}/p001"
    
    try:
        anno_resp = requests.get(annotations_api, verify=False, timeout=10)
        if anno_resp.status_code == 404:
            print("⚠️ Page 1 OCR not found. This is expected if the record has no HOCR data.")
            page_text = "<NO OCR DATA AVAILABLE FOR THIS RECORD>"
        else:
            anno_resp.raise_for_status()
            anno_data = anno_resp.json()
            
            # Extract text from the AnnotationList
            words = []
            for resource in anno_data.get("resources", []):
                chars = resource.get("resource", {}).get("chars", "")
                if chars:
                    words.append(chars)
                    
            page_text = " ".join(words)
            print(f"✅ Successfully extracted {len(page_text)} characters of OCR text.")
    except Exception as e:
        print(f"❌ Failed to fetch OCR annotations: {e}")
        return

    # 3. Simulate RAG Context Generation
    print("\n[Step 3] Generating LLM Prompt Context...")
    
    context_block = f"""
=================================================================
DOCUMENT CONTEXT FOR LLM (RAG)
=================================================================

METADATA:
---------
Title: {title}
Record ID (PID): {pid}

DESCRIPTION:
------------
{description}

CONTENT (PAGE 1):
-----------------
{page_text[:500]}{'...' if len(page_text) > 500 else ''}
=================================================================
"""
    print(context_block)
    print("✅ RAG Feasibility Test Complete.")

def main():
    parser = argparse.ArgumentParser(description="Run RAG Feasibility Test")
    parser.add_argument("--target", choices=["local", "prod"], default="local", 
                        help="Target environment to test (default: local)")
    args = parser.parse_args()

    if args.target == "prod":
        base_url = "https://invenio.turath-project.com"
        # Assuming prod IIIF search runs on same domain, port 5001 or standard 443 depending on Nginx
        # We default to 5001 here, but note that prod architecture might proxy this differently
        iiif_url = "https://invenio.turath-project.com:5001" 
    else:
        base_url = "https://127.0.0.1:5000"
        iiif_url = "https://127.0.0.1:5001"

    run_rag_test(base_url, iiif_url)

if __name__ == "__main__":
    main()
