from bs4 import BeautifulSoup
import requests
import urllib.parse
import stealth

class DetikScraper:
    BASE_URL = "https://www.detik.com/search/searchall"

    def search(self, query, detail=False, limit=None):
        params = {
            'query': query,
            'siteid': '2' # Site ID 2 is usually detiknews
        }
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        headers = stealth.get_headers()
        stealth.random_delay()
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            # Target the new article structure
            items = soup.find_all('article')
            
            for item in items:
                try:
                    title_elm = item.find(class_='title') or item.find(class_='media__title') or item.find('h3') or item.find('h2')
                    link_elm = item.find('a')
                    img_elm = item.find('img')
                    date_elm = item.find(class_='date') or item.find(class_='media__date')

                    if title_elm and link_elm:
                        article = {
                            'judul': title_elm.get_text(strip=True),
                            'link': link_elm['href'],
                            'gambar': img_elm['src'] if img_elm else None,
                            'waktu': date_elm.get_text(strip=True) if date_elm else None,
                            'body': '' # Detail not implemented to keep it simple/fast
                        }
                        articles.append(article)
                except Exception:
                    continue
            
            if limit:
                articles = articles[:limit]
                
            return articles
            
        except Exception as e:
            print(f"Error scraping Detik: {e}")
            return []

    def get_article(self, url):
        headers = stealth.get_headers()
        stealth.random_delay()
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            title_elm = soup.find('h1')
            title = title_elm.get_text(strip=True) if title_elm else ""
            
            # Image
            img_elm = soup.find('img', class_='detail__media-image') or soup.find('div', class_='detail__media').find('img') if soup.find('div', class_='detail__media') else None
            if not img_elm:
                 # Fallback generic
                 img_elm = soup.find('img')
            
            image = img_elm['src'] if img_elm else ""
            
            # Body
            # Try multiple common Detik body classes
            body_elm = soup.find('div', class_='detail__body-text') or \
                       soup.find('div', class_='itp_bodycontent') or \
                       soup.find('div', class_='read__content')
                       
            if body_elm:
                # Remove unwanted elements (ads, read also, etc)
                for unwanted in body_elm.find_all(['script', 'style', 'div', 'iframe']):
                    unwanted.decompose()
                body = body_elm.get_text(separator='\n\n', strip=True)
            else:
                body = "Konten tidak ditemukan atau structure berubah."

            return {
                "judul": title,
                "poster": image,
                "body": body,
                "link": url
            }
            
        except Exception as e:
            return {"error": str(e)}
