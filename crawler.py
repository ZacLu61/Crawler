import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import cn2an

from text_extractor import TextExtractor

valid_url_header = "https://www.mei8888.com/%e"
max_pages_count = 100

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        # self.order_context = dict()
        self.urls_to_visit = [base_url]

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_links(self, html_content, base_url):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            links.add(full_url)
        return links

    def crawl(self, max_pages_count=50):
        while self.urls_to_visit and len(self.visited_urls) < max_pages_count:
            current_url = self.urls_to_visit.pop(0)
            if current_url in self.visited_urls:
                continue
            
            if not current_url.startswith(valid_url_header):
                continue

            print(f"Crawling: {current_url}")
            html_content = self.fetch_page(current_url)
            if not html_content:
                continue

            links = self.parse_links(html_content, current_url)
            self.urls_to_visit.extend(links - self.visited_urls)
            self.visited_urls.add(current_url)
        return self.visited_urls

    def add_to_order_context(self, urls):
        ordered_context = dict()
        for url in urls:
            extractor = TextExtractor(url)
            text = extractor.get_text_from_website()
            title = re.search("第.*章", text).group()
            # print(title)
            title_to_num = cn2an.cn2an(title[1:-1], "smart")
            # print(title_to_num)
            ordered_context[title_to_num] = text
        return ordered_context
        
        
if __name__ == "__main__":
    base_url = "https://www.mei8888.com/%e7%ac%ac%e4%b8%80%e7%99%be%e5%85%ab%e5%8d%81%e5%9b%9b%e7%ab%a0-%e5%a0%82%e8%80%8c%e7%9a%87%e4%b9%8b%e7%9a%84%e5%81%8f%e6%84%9b/"
    crawler = WebCrawler(base_url)
    visited_urls = crawler.crawl(max_pages_count)
    order_context = crawler.add_to_order_context(visited_urls)
    
    f = open("novel.txt", "w")
    
    # print("order_context")
    # print(order_context)
    print("Visited URLs:")
    
    for index in range(1, 1000):
        if index not in order_context:
            continue
        # print("index:{}".format(index))
        # print(order_context[index])
        f.write(order_context[index])
    
    
    # for url in visited_urls:
    #     print(url)
        
        # if index not in order_context:
        #     continue
        
         
        # extractor = TextExtractor(url)
        # text = extractor.get_text_from_website()
        # print("Extracted Text:")        
        # print(text)
        # break
        
    # f.write(text)    
    f.close()
