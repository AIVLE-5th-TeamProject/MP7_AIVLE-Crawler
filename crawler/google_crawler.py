import os
import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from config import config


class GoogleCrawler:
    def __init__(self, k):
        self.driver_path = config['path']['chrome_driver']
        self.url = config['url']['google_search']
        self.output_directory = config['path']['output_directory']
        self.search_result_selector = config['selector']['search_result']
        self.k = k
        self.driver = self.get_chrome_driver()

    def get_chrome_driver(self):
        """ 크롬 드라이버 객체를 생성하는 함수 """
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-cache')
        options.add_argument('--headless')

        try:
            service = Service(executable_path=self.driver_path)
            driver = webdriver.Chrome(options=options, service=service)
        except Exception as e:
            print(f"Error using existing driver: {e}")

            if os.path.exists(self.driver_path):
                os.remove(self.driver_path)

            new_driver_path = ChromeDriverManager().install()
            service = Service(executable_path=new_driver_path)
            driver = webdriver.Chrome(options=options, service=service)

        return driver

    def wait_for_element(self, by_type, identifier, timeout=10):
        """ 웹 페이지에 특정 요소가 완전히 로드될 때까지 대기하는 함수 """
        try:
            wait_element = WebDriverWait(self.driver, timeout)
            element = wait_element.until(EC.presence_of_element_located((by_type, identifier)))
            return element
        except TimeoutException:
            return None

    def extract_search_results(self):
        """구글 검색 결과 페이지에서 링크 추출"""
        self.driver.get(self.url)
        self.wait_for_element(By.CSS_SELECTOR, self.search_result_selector)

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

    def wait_for_page_load(self, timeout=30):
        """ 페이지 전체가 완전히 로드될 때까지 대기하는 함수 """
        def page_load_condition(d):
            script = "return document.readyState === 'complete'"
            return d.execute_script(script)
        WebDriverWait(self.driver, timeout).until(page_load_condition)

    def save_to_csv(self, data):
        """크롤링한 데이터를 CSV 파일로 저장하는 함수"""
        current_time = time.strftime("%Y%m%d_%H%M")
        filename = f'search_{current_time}.csv'
        filepath = os.path.join(self.output_directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'content', 'url'])
            writer.writeheader()
            writer.writerows(data)

    def crawl(self):
        """크롤링 수행 함수"""
        start_time = time.time()

        results = self.extract_search_results()
        all_posts = []

        for result in results:
            post = self.extract_post_content(result)
            all_posts.append(post)

        self.driver.quit()

        self.save_to_csv(all_posts)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"소요 시간: {elapsed_time:.2f}초")


if __name__ == "__main__":
    k = int(input("크롤링할 상위 검색 결과의 개수를 입력하세요: "))
    crawler = GoogleCrawler(k)
    crawler.crawl()
