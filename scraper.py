
import requests
from bs4 import BeautifulSoup

def scrape_generic_info(url):
    """
    Scrapes the title and main text from a given URL.
    This is a fallback method and may not work for all sites.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get Title
        title = soup.title.string if soup.title else ""
        
        # Get meta description
        meta_desc = ""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            meta_desc = meta.get('content', '')
            
        # Get first few paragraphs or H1
        h1 = soup.find('h1')
        h1_text = h1.get_text().strip() if h1 else ""
        
        # Combine info
        extracted_text = f"Title: {title}\nDescription: {meta_desc}\nH1: {h1_text}"
        return extracted_text
        
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None
