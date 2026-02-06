import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

GATEWAY_URL = "http://localhost:4000"

# Defined based on source code analysis
ENDPOINTS = [
    # API Berita Indonesia (RSS)
    "/rss/cnn/terbaru", "/rss/cnn/nasional", "/rss/cnn/internasional", "/rss/cnn/ekonomi",
    "/rss/cnn/olahraga", "/rss/cnn/teknologi", "/rss/cnn/hiburan", "/rss/cnn/gayaHidup",
    
    "/rss/antara/terbaru", "/rss/antara/politik", "/rss/antara/hukum", "/rss/antara/ekonomi",
    "/rss/antara/metro", "/rss/antara/bola", "/rss/antara/olahraga", "/rss/antara/humaniora",
    "/rss/antara/lifestyle", "/rss/antara/hiburan", "/rss/antara/dunia", "/rss/antara/tekno",
    "/rss/antara/otomotif",

    "/rss/cnbc/terbaru", "/rss/cnbc/investment", "/rss/cnbc/news", "/rss/cnbc/market",
    "/rss/cnbc/entrepreneur", "/rss/cnbc/syariah", "/rss/cnbc/tech", "/rss/cnbc/lifestyle",
    "/rss/cnbc/opini", "/rss/cnbc/profil",

    # CNN Indonesia News API (Scraper)
    "/cnn-api/nasional", "/cnn-api/internasional", "/cnn-api/ekonomi", "/cnn-api/olahraga",
    "/cnn-api/teknologi", "/cnn-api/hiburan", "/cnn-api/gaya-hidup",
    
    # Detik News API (Search) - using generic terms to simulate news feed
    "/detik/search?q=indonesia", "/detik/search?q=jakarta", "/detik/search?q=ekonomi",

    # Berita Indo API (Next.js) - Complete list
    "/berita-indo/api/cnn-news/", 
    "/berita-indo/api/cnbc-news/", 
    "/berita-indo/api/kumparan-news/",
    "/berita-indo/api/tribun-news/",
    "/berita-indo/api/republika-news/",
    "/berita-indo/api/okezone-news/",
    "/berita-indo/api/vice-news/",
    "/berita-indo/api/antara-news/",
    "/berita-indo/api/suara-news/",
    "/berita-indo/api/tempo-news/",
    "/berita-indo/api/voa-news/",
    "/berita-indo/api/zetizen-jawapos-news/",
    
    # --- UNIFIED SMART ENDPOINTS ---
    "/api/search?q=indonesia",
    "/api/category/nasional",
    "/api/category/teknologi",
    "/api/category/ekonomi" 
]

def fetch_count(endpoint):
    url = f"{GATEWAY_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        count = 0
        
        # Determine count based on response structure
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                count = len(data['data'])
            elif 'length' in data:
                count = int(data['length'])
            elif 'total' in data:
                count = int(data['total'])
            # Berita Indo API structure check
            elif 'posts' in data: 
                count = len(data['posts'])
                
        return endpoint, count, "OK"
    except Exception as e:
        return endpoint, 0, str(e)

print(f"Benchmarking {len(ENDPOINTS)} endpoints via Gateway ({GATEWAY_URL})...")
print("-" * 80)
print(f"{'Endpoint':<40} | {'Count':<6} | {'Status'}")
print("-" * 80)

total_articles = 0
start_time = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_count, ep): ep for ep in ENDPOINTS}
    
    for future in as_completed(futures):
        ep, count, status = future.result()
        if len(status) > 30: status = status[:27] + "..."
        print(f"{ep:<40} | {count:<6} | {status}")
        total_articles += count

duration = time.time() - start_time
print("-" * 80)
print(f"GRAND TOTAL: {total_articles} articles found")
print(f"Time Taken: {duration:.2f} seconds")
