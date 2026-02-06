import requests
import time
import json

GATEWAY = "http://localhost:4000"

def log(name, status, details=""):
    print(f"[{'PASS' if status else 'FAIL'}] {name:<25} {details}")

def test_search():
    print("\n--- Testing SEARCH Features ---")
    
    # 1. Detik Search
    try:
        r = requests.get(f"{GATEWAY}/detik/search?q=jokowi")
        data = r.json()
        success = r.status_code == 200 and 'data' in data and len(data['data']) > 0
        log("Detik Search", success, f"Found {len(data.get('data', []))} articles" if success else str(data))
    except Exception as e:
        log("Detik Search", False, str(e))

    # 2. CNN Search
    try:
        # Check /cnn-api/search/?q=...
        r = requests.get(f"{GATEWAY}/cnn-api/search/?q=ekonomi")
        data = r.json()
        # CNN API usually returns list inside 'data' or directly if custom response structure checking needed
        # Based on code.py, it returns list of dicts. Res.success wraps it in standard response? 
        # main.py: return res.success(response) -> probably {'status': 200, 'values': [...]} or similar.
        # Let's inspect raw first to be safe.
        success = r.status_code == 200
        count = 0
        if success:
            if 'values' in data: count = len(data['values']) # Common flask wrapper pattern
            elif 'data' in data: count = len(data['data'])
            else: count = len(data) if isinstance(data, list) else 0
            
        log("CNN Search", success and count > 0, f"Found {count} articles")
    except Exception as e:
        log("CNN Search", False, str(e))

def test_categories():
    print("\n--- Testing CATEGORY Features ---")
    
    endpoints = [
        ("/cnn-api/nasional", "CNN Nasional"),
        ("/cnn-api/teknologi", "CNN Teknologi"),
        ("/rss/cnn/terbaru", "RSS CNN Terbaru"),
        ("/rss/antara/politik", "RSS Antara Politik"),
        ("/rss/cnbc/market", "RSS CNBC Market")
    ]
    
    for ep, name in endpoints:
        try:
            r = requests.get(f"{GATEWAY}{ep}")
            data = r.json()
            # RSS returns {success: true, data: [...]}
            # CNN returns { ... } (wrapper)
            
            count = 0
            if 'data' in data: count = len(data['data'])
            elif 'values' in data: count = len(data['values'])
            elif isinstance(data, list): count = len(data)
            
            log(name, r.status_code == 200 and count > 0, f"Found {count} items")
        except Exception as e:
            log(name, False, str(e))

def test_details():
    print("\n--- Testing DETAIL Features ---")
    
    # Detik Detail Flow
    detik_link = None
    try:
        # Get a link first
        r = requests.get(f"{GATEWAY}/detik/search?q=jakarta")
        data = r.json()
        if 'data' in data and data['data']:
            detik_link = data['data'][0]['link']
    except: pass
    
    if detik_link:
        try:
            r = requests.get(f"{GATEWAY}/detik-detail?url={detik_link}")
            d = r.json()
            body_len = len(d.get('data', {}).get('body', ''))
            log("Detik Detail", r.status_code == 200 and body_len > 100, f"Body length: {body_len}")
        except Exception as e:
             log("Detik Detail", False, str(e))
    else:
        log("Detik Detail", False, "Skipped (No link found)")

    # CNN Detail Flow
    cnn_link = None
    try:
        r = requests.get(f"{GATEWAY}/rss/cnn/terbaru")
        data = r.json()
        if 'data' in data and data['data']:
            cnn_link = data['data'][0]['link']
    except: pass
    
    if cnn_link:
        try:
            # RSS link might need cleaning or direct usage
            r = requests.get(f"{GATEWAY}/cnn-detail?url={cnn_link}")
            d = r.json()
            # Check structure based on code.py
            # Gateway proxies /cnn-api/detail/ -> returns list of dicts or wrapper?
            # code.py detail() returns data list. res.success() wraps it.
            # Assuming 'values' or 'data'.
            
            # Note: verify_details.py output showed 'data' was a list.
            
            items = d.get('data', []) or d.get('values', [])
            if isinstance(items, list) and len(items) > 0:
                body_len = len(items[0].get('body', ''))
                log("CNN Detail", r.status_code == 200 and body_len > 10, f"Body length: {body_len}")
            else:
                 log("CNN Detail", False, f"Empty or invalid data: {str(d)[:100]}")
        except Exception as e:
            log("CNN Detail", False, str(e))
    else:
        log("CNN Detail", False, "Skipped (No link found)")

if __name__ == "__main__":
    time.sleep(2) # Warmup
    test_search()
    test_categories()
    test_details()
