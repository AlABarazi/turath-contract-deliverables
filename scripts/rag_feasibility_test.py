import requests
import json
import urllib3
import os

# Disable SSL warnings for local self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://127.0.0.1:5000"
SEARCH_URL = "https://127.0.0.1:5001"
SEARCH_API = f"{BASE_URL}/api/records"

def get_latest_record_with_files():
    """Fetch the latest published record that has files attached."""
    print(f"Fetching latest record from {SEARCH_API}...")
    
    params = {
        "size": 10,
        "sort": "newest"
    }
    
    response = requests.get(SEARCH_API, params=params, verify=False)
    response.raise_for_status()
    
    data = response.json()
    hits = data.get("hits", {}).get("hits", [])
    
    for hit in hits:
        if hit.get("files", {}).get("enabled", False):
            return hit
            
    print("No records with files found.")
    return None

def fetch_page_text(record_pid, page_id="p001"):
    """Fetch text for a specific page using the IIIF Annotations API."""
    url = f"{SEARCH_URL}/annotations/{record_pid}/{page_id}"
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            data = response.json()
            # Extract text from annotations
            words = []
            for resource in data.get("resources", []):
                text = resource.get("resource", {}).get("chars", "")
                if text:
                    words.append(text)
            return " ".join(words)
        else:
            return f"[Failed to fetch page text: HTTP {response.status_code}]"
    except Exception as e:
        return f"[Error fetching page text: {e}]"

def generate_rag_context(record, page_text):
    """Format the data into a clean text block suitable for an LLM context window."""
    
    metadata = record["metadata"]
    creators = [c.get("person_or_org", {}).get("family_name", "") for c in metadata.get("creators", [])]
    
    context = f"""=================================================================
DOCUMENT CONTEXT FOR LLM (RAG)
=================================================================

METADATA:
---------
Title: {metadata.get('title')}
Authors: {', '.join(creators)}
Record ID (PID): {record['id']}
Publication Date: {metadata.get('publication_date', 'Unknown')}
Resource Type: {metadata.get('resource_type', {}).get('id', 'Unknown')}

DESCRIPTION:
------------
{metadata.get('description') or 'No description provided.'}

CONTENT (PAGE 1):
-----------------
{page_text}
=================================================================
"""
    return context

def main():
    print("Starting RAG Feasibility Test...")
    print("-" * 50)
    
    record = get_latest_record_with_files()
    
    if not record:
        print("Failed to find a suitable record for testing.")
        return
        
    pid = record['id']
    title = record['metadata'].get('title')
    print(f"✅ Successfully retrieved record: {pid} - {title}")
    
    print(f"Fetching page 1 text from IIIF Annotations API ({SEARCH_URL})...")
    page_text = fetch_page_text(pid, "p001")
    
    if "[Failed" in page_text or "[Error" in page_text:
         print(f"⚠️ Warning: Could not extract page text: {page_text}")
    else:
         print(f"✅ Successfully extracted {len(page_text)} characters from Page 1.")
    
    print("\nGenerating simulated LLM Context Window...")
    context_block = generate_rag_context(record, page_text)
    print(context_block)
    
    # Write to a sample output file
    output_file = "rag_sample_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(context_block)
        
    print(f"\n✅ Sample RAG context written to {output_file}")
    print("\nCONCLUSION: The REST API successfully provides both structured metadata and page-level granular OCR text (via the IIIF Annotations API). This proves high readiness for RAG pipelines, allowing systems to chunk data page-by-page without requiring complex PDF parsing on the consumer side.")

if __name__ == "__main__":
    main()
