from bs4 import BeautifulSoup
from requests import get
from requests import get
# FIXED: Relative import for Vercel structure
try:
    from . import stealth
except ImportError:
    import stealth

base_url = 'https://www.cnnindonesia.com'

class CNN:
    """
    Mengambil berbagai berita dari website cnnindonesia.com
    
    Contoh:
        - mengambil berita internasional
        from src import cnn

        print(cnn.berita_internasional())
    """

    def query(self, url):
        """
        Mengambil data dari body berita
        
        :param url: url yang datanya ingin diambil
        :return: list dictionaries.
        """

        stealth.random_delay()
        headers = stealth.get_headers()
        datas = get(url, headers=headers)
        soup = BeautifulSoup(datas.text, 'html.parser')
        
        # Updated selector logic for new CNN Indonesia layout (Tailwind)
        # Parent container is now generic grid, so we find all articles directly
        tag = soup.find_all("article")
        data = []

        for i in tag:
            try:
                # Title is usually in h2, sometimes h1
                title_tag = i.find("h2")
                if not title_tag:
                    title_tag = i.find("h1")
                
                title = title_tag.text.strip() if title_tag else ""
                
                # Link is in the first anchor tag
                link_tag = i.find('a')
                link = link_tag['href'].strip() if link_tag else ""
                
                # Image is in the first img tag
                img_tag = i.find('img')
                gambar = img_tag['src'].strip() if img_tag else ""
                
                # Filter out empty data
                if title and link:
                    data.append({
                        "judul": title,
                        "link": link,
                        "poster": gambar,
                        "tipe": "Berita", # Generic type as specific class is harder to find now
                        "waktu": "" # Time is often dynamic/relative, leaving empty for now to avoid crash
                    })
            except Exception as e:
                # print(f"Error parsing article: {e}")
                pass

        return data

    def index(self):
        """
        It returns the result of the query of the home news from cnn's site
        :return: The response object.
        """
        return self.query('{}/'.format(base_url))

    def berita_nasional(self):
        """
        Mengambil berita nasional

        :return: list dictionary
        """
        return self.query('{}/nasional'.format(base_url))

    def berita_internasional(self):
        """
        Mengambil berita internasional / luar negeri
        
        :return: list dictionary
        """
        return self.query('{}/internasional'.format(base_url))

    def berita_ekonomi(self):
        """
        Mengambil berita ekonomi
        
        :return: list dictionary
        """
        return self.query('{}/ekonomi'.format(base_url))

    def berita_olahraga(self):
        """
        Mengambil berita olahraga
        
        :return: list dictionary
        """
        return self.query('{}/olahraga'.format(base_url))

    def berita_teknologi(self):
        """
        Mengambil berita teknologi
        
        :return: list dictionary
        """
        return self.query('{}/teknologi'.format(base_url))

    def berita_hiburan(self):
        """
        Mengambil berita hiburan
        
        :return: list dictionary
        """
        return self.query('{}/hiburan'.format(base_url))

    def berita_social(self):
        """
        Mengambil berita sosial
        
        :return: list dictionary
        """
        return self.query('{}/gaya-hidup'.format(base_url))

    def detail(self, url):
        """
        Mengambil detail berita
        :args:
            url : string -> url berita
        :example:
            url : string -> https://www.cnnindonesia.com/teknologi/20220921153459-190-850830/cara-menghapus-data-iphone-sebelum-dijual
        :return: list dictionary
        """
        data = []
        try:
            stealth.random_delay()
            req = get(url, headers=stealth.get_headers())
            soup = BeautifulSoup(req.text, 'html.parser')
            
            # Robust selectors for body
            tag = soup.find('div', class_="detail_text") or \
                  soup.find('div', class_="detail-text") or \
                  soup.find('div', class_="read__content") or \
                  soup.find('div', class_="itp_bodycontent")
            
            # Image
            gambar_tag = soup.find('div', class_='media_artikel')
            gambar = gambar_tag.find('img').get('src') if gambar_tag and gambar_tag.find('img') else ""
            if not gambar:
                 img = soup.find('img')
                 gambar = img['src'] if img else ""

            # Title
            judul_tag = soup.find('h1', class_='title') or soup.find('h1')
            judul = judul_tag.text.strip() if judul_tag else ""
            
            body = tag.get_text(separator='\n\n', strip=True) if tag else "Konten tidak ditemukan"
            
            data.append({
                "judul": judul,
                "poster": gambar,
                "body": body,
            })
        except:
            data.append({
                "message": "network error",
            })

        return data

    def search(self,q):
        """
        Mencari berita spesifik berdasarkan query

        :args:
            q : string -> query atau berita yang ingin dicari
        :returns: list dictionary
        """

        return self.query('{}/search/?query={}'.format(base_url, q))

if __name__ != '__main__':
    cnn = CNN()