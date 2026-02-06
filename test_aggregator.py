import requests
import json
import time

GATEWAY = "http://localhost:4000"

def test_search(query):
    print(f"\n[TEST] Unified Search: {query}")
    try:
        r = requests.get(f"{GATEWAY}/api/search?q={query}")
        data = r.json()
        
        if r.status_code == 200:
            print(f"Status: OK | Total: {data.get('total')}")
            items = data.get('data', [])
            sources = set(i.get('source') for i in items)
            print(f"Sources Found: {sources}")
            
            if items:
                print(f"Sample: {items[0]['title']} ({items[0]['source']})")
        else:
            print(f"FAILED: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_category(cat):
    print(f"\n[TEST] Unified Category: {cat}")
    try:
        r = requests.get(f"{GATEWAY}/api/category/{cat}")
        data = r.json()
        
        if r.status_code == 200:
            print(f"Status: OK | Total: {data.get('total')}")
            items = data.get('data', [])
            sources = {}
            for i in items:
                s = i.get('source')
                sources[s] = sources.get(s, 0) + 1
            print(f"Sources Found: {sources}")
            
            # Verify schema
            if items:
                i = items[0]
                print(f"Schema Check: Title={bool(i['title'])}, Link={bool(i['link'])}, Image={bool(i['image'])}, Time={bool(i['time'])}")
        else:
            print(f"FAILED: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    time.sleep(2) # Warmup
    test_search("indonesia")
    test_category("teknologi")
    test_category("nasional")
