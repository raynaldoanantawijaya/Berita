import requests
import time

GATEWAY = "http://localhost:4000"

def test_cnn():
    print("\n--- Testing CNN Detail ---")
    try:
        # 1. Get List
        r = requests.get(f"{GATEWAY}/rss/cnn/terbaru")
        idx = r.json()
        if 'data' in idx and len(idx['data']) > 0:
            link = idx['data'][0]['link']
            print(f"Target URL: {link}")
            
            # 2. Get Detail
            # Note: Gateway map is /cnn-detail?url=... which maps to /cnn-api/detail/?url=...
            # The Gateway config in server.js says: 'cnn-detail': '/cnn-api/detail/?url=...'
            # This means valid request is http://localhost:4000/cnn-detail?url=...
            
            # Wait a bit to ensure server is up
            time.sleep(1)
            detail_url = f"{GATEWAY}/cnn-detail?url={link}"
            r2 = requests.get(detail_url)
            
            print(f"Status: {r2.status_code}")
            data = r2.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"Title: {data[0].get('judul')}")
                print(f"Body Length: {len(data[0].get('body', ''))}")
                print(f"Snippet: {data[0].get('body', '')[:100]}...")
            else:
                print("Failed to get detail data")
        else:
            print("Failed to get CNN list")
    except Exception as e:
        print(f"Error: {e}")

def test_detik():
    print("\n--- Testing Detik Detail ---")
    try:
        # 1. Get Search List
        r = requests.get(f"{GATEWAY}/detik/search?q=indonesia")
        data = r.json()
        if 'data' in data and len(data['data']) > 0:
            link = data['data'][0]['link']
            print(f"Target URL: {link}")
            
            time.sleep(1)
            detail_url = f"{GATEWAY}/detik-detail?url={link}"
            r2 = requests.get(detail_url)
            
            print(f"Status: {r2.status_code}")
            d = r2.json()
            if 'data' in d:
                art = d['data']
                print(f"Title: {art.get('judul')}")
                print(f"Body Length: {len(art.get('body', ''))}")
                print(f"Snippet: {art.get('body', '')[:100]}...")
            else:
                print("Failed to get detail data")
        else:
            print("Failed to get Detik list")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    time.sleep(3) # Wait for services to warm up
    test_cnn()
    test_detik()
