import requests

urls = [
    'https://thelazymedia.com/',
    'https://www.cnnindonesia.com/rss',
    'https://www.cnnindonesia.com/nasional/rss'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

for url in urls:
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        print(f"Length: {len(r.text)}")
        if r.status_code == 200:
            print("Snippet: ", r.text[:200])
        print("-" * 20)
    except Exception as e:
        print(f"Error checking {url}: {e}")
