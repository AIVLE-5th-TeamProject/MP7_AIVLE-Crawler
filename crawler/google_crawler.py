import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from base_crawler import BaseCrawler
from config import config


class GoogleCrawler(BaseCrawler):
    def __init__(self, k):
        super().__init__(config['path']['chrome_driver'], config['path']['output_directory'])
        self.url = config['url']['google_search']
        self.search_result_selector = config['selector']['search_result']
        self.k = k

    def extract_search_results(self):
        """구글 검색 결과 페이지에서 링크 추출"""
        self.driver.get(self.url)
        self.wait_for_element('locate', By.CSS_SELECTOR, self.search_result_selector)

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        results = []
        for a_tag in soup.select(self.search_result_selector):
            link = a_tag['href']
            results.append(link)
            if len(results) >= self.k:
                break

        return results

    def extract_post_content(self, url):
        """단일 게시물의 내용을 추출"""
        self.driver.get(url)
        self.wait_for_page_load()

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else 'No Title'
        content = ' '.join([p.text for p in soup.find_all('p')])

        return {'title': title, 'content': content, 'url': url}

    def crawl(self):
        """크롤링 수행 함수"""
        start_time = time.time()

        results = self.extract_search_results()
        all_posts = []

        for result in results:
            post = self.extract_post_content(result)
            all_posts.append(post)

        self.driver.quit()

        # 데이터를 CSV 파일로 저장
        current_time = time.strftime("%Y%m%d_%H%M")
        filename = f'search_{current_time}.csv'
        self.save_to_csv(all_posts, filename)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"소요 시간: {elapsed_time:.2f}초")


if __name__ == "__main__":
    k = int(input("크롤링할 상위 검색 결과의 개수를 입력하세요: "))
    crawler = GoogleCrawler(k)
    crawler.crawl()
