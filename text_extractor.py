import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class TextExtractor:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.urls_to_visit = [base_url]

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Get the text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())

        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text

    def get_text_from_website(self):
        html_content = self.fetch_page(self.base_url)
        if html_content:
            return self.extract_text(html_content)
        return ""
    
    def parse_links(self, html_content, base_url):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            links.add(full_url)
        return links

    def crawl(self, max_pages=50):
        while self.urls_to_visit and len(self.visited_urls) < max_pages:
            current_url = self.urls_to_visit.pop(0)
            if current_url in self.visited_urls:
                continue

            print(f"Crawling: {current_url}")
            html_content = self.fetch_page(current_url)
            if not html_content:
                continue

            links = self.parse_links(html_content, current_url)
            self.urls_to_visit.extend(links - self.visited_urls)
            self.visited_urls.add(current_url)

        return self.visited_urls