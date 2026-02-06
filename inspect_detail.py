import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def inspect(url, name):
    print(f"--- Inspecting {name} ---")
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Title
        h1 = soup.find('h1')
        print(f"H1: {h1.get_text(strip=True) if h1 else 'Not Found'}")
        
        # Image
        img = soup.find('img') # simplistic, usually needs a class
        print(f"First Img: {img['src'] if img else 'Not Found'}")
        
        # Body candidates
        # CNN often uses: detail-text, read__content
        # Detik often uses: detail__body-text, itp_bodycontent
        candidates = ['detail-text', 'read__content', 'detail__body-text', 'itp_bodycontent', 'detail_text']
        
        for c in candidates:
            found = soup.find(class_=c)
            if found:
                print(f"Found Body Container: .{c}")
                print(f"Snippet: {found.get_text(strip=True)[:100]}...")
                
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

# Use real recent URLs (generic placeholders might fail if 404)
# I will try to fetch the RSS feed first to get a valid URL, or just use the homepage to find one.

# Fetch a valid CNN URL from RSS
try:
    rss = requests.get('https://www.cnnindonesia.com/rss', headers=headers)
    soup = BeautifulSoup(rss.text, 'xml')
    item = soup.find('item')
    if item:
        link = item.find('link').text
        inspect(link, "CNN Indonesia")
except:
    print("Failed to fetch CNN RSS")

# Fetch a valid Detik URL
try:
    r = requests.get('https://www.detik.com/', headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Find a news link
    a = soup.find('article').find('a')
    if a:
        inspect(a['href'], "Detik")
except:
    print("Failed to fetch Detik Homepage")
