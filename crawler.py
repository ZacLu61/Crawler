import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import cn2an
# from selenium.webdriver.chrome.options import Options
# from selenium import webdriver
from text_extractor import TextExtractor
from datetime import datetime

# base_url = "https://www.mei8888.com/%e7%ac%ac1%e7%ab%a0-%e6%ad%b9%e6%af%92%e8%b3%a3%e5%ad%90/"
# base_url = "https://acg1213.com/book_ZnRtdmZFSzN3RGNhblRuOUcvZldHZz09?su=5D1DC277#stwjxjc"
# valid_url_header = "https://www.mei8888.com/%e"
valid_url_header = "https://acg1213.com/book"
# max_pages_count = 50

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.ordered_context = dict()
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
        links = set()
        soup = BeautifulSoup(html_content, 'html.parser')
        context = soup.find('li', attrs={'class': 'nextp'})
        print("context !!!")
        print(context)
        
        # print("parsed start !!!")
        
        prefix = "<a onclick=\"JumpUrl('"
        suffix = "')\">"

        for text in context:
            text = str(text)
            if text.startswith(prefix):
                start_index = text.index(prefix)
                end_index = text.index(suffix)
                url = text[start_index+len(prefix):end_index]
                links.add(url)
                
        # print("parsed end !!!")   
        
        return links

        # soup = BeautifulSoup(html_content, 'html.parser')
        # links = set()
        # for link in soup.find_all('a', href=True):
        #     full_url = urljoin(base_url, link['href'])
        #     links.add(full_url)
        # return links

    def crawl(self, max_pages_count=50):
        print("Crawling start!!!")
        
        crawler_count = 1
        
        while self.urls_to_visit and len(self.visited_urls) < max_pages_count:
            current_url = self.urls_to_visit.pop(0)
            
            if not current_url.startswith(valid_url_header):
                continue

            if current_url in self.visited_urls:
                continue

            print("Count:", crawler_count)
            crawler_count += 1
            print(f"Crawling: {current_url}\n")
            html_content = self.fetch_page(current_url)
            if not html_content:
                continue

            links = self.parse_links(html_content, current_url)
            
            # print("links", links)
            
            self.urls_to_visit.extend(links - self.visited_urls)
            self.visited_urls.add(current_url)
            
        print("Crawling end!!!")
        return self.visited_urls
        

    def add_to_order_context(self, urls):
        print("add_to_order_context start!!!")

        self.ordered_context = dict()
        for url in urls:
            extractor = TextExtractor(url)
            text = extractor.get_text_from_website()
            title = re.search("第.*章", text).group()
            title_to_num = cn2an.cn2an(title[1:-1], "smart")
            self.ordered_context[title_to_num] = text
            
        print("add_to_order_context end!!!")

        return self.ordered_context
        
        
if __name__ == "__main__":
    global base_url
    base_url = input("請輸入網址：")
    global max_pages_count
    max_pages_count = int(input("請輸入最大頁數："))
    
    start_time = datetime.now()
    
    crawler = WebCrawler(base_url)
    visited_urls = crawler.crawl(max_pages_count)
    order_context = crawler.add_to_order_context(visited_urls)
    
    f = open("novel.txt", "w")
    print("Visited URLs:")
    
    for index in range(1, 1000):
        if index not in order_context:
            continue
        f.write("\n\n\n第{}章\n\n\n".format(cn2an.an2cn(index, "low")))
        f.write(order_context[index])
        
    f.close()
    
    duration = datetime.now() - start_time
    
    print("------ Duration: {} -----\n".format(duration))
