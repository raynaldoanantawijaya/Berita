import requests
from bs4 import BeautifulSoup

url = 'https://www.cnnindonesia.com/search/?query=ekonomi'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

try:
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Check for Next.js data
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("Found __NEXT_DATA__!")
        print(next_data.string[:500])
    else:
        print("No __NEXT_DATA__ found")
        
    articles = soup.find_all('article')
    print(f"Articles found: {len(articles)}")

except Exception as e:
    print(e)
