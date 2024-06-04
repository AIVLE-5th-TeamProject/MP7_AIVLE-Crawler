import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from base_crawler import BaseCrawler
from config import config


class AivleCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(config['path']['chrome_driver'], config['path']['output_directory'])
        self.url = config['url']['aivle_url']
        self.faq_list_selector = config['selector']['faq_list']
        self.category_selector = config['selector']['category']
        self.question_selector = config['selector']['question']
        self.answer_selector = config['selector']['answer']
        self.more_button_selector = config['selector']['more_button']

    def extract_faq_data(self, existing_data):
        """현재 페이지의 FAQ 데이터를 추출하는 함수"""
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        faqs = []
        faq_items = soup.select(self.faq_list_selector)

        for item in faq_items:
            category = item.select_one(self.category_selector).text.strip()
            question = item.select_one(self.question_selector).text.strip()
            answer = item.select_one(self.answer_selector).text.strip()

            faq = {
                'category': category,
                'content': f"{question}\n{answer}"
            }

            if faq not in existing_data:  # 기존 데이터와 중복 여부 확인
                faqs.append(faq)

        return faqs

    def crawl(self):
        """크롤링 수행 함수"""
        start_time = time.time()

        self.driver.get(self.url)
        self.wait_for_page_load()

        all_faqs = []

        # '더보기' 버튼을 클릭하여 모든 데이터를 로드
        while True:
            try:
                # 현재 페이지의 FAQ 데이터 추출 및 중복 확인
                faqs = self.extract_faq_data(all_faqs)
                all_faqs.extend(faqs)

                # '더보기' 버튼을 찾아 클릭
                more_button = self.wait_for_element('click', By.CSS_SELECTOR, self.more_button_selector)
                if more_button:
                    self.driver.execute_script("arguments[0].click();", more_button)
                    self.wait_for_page_load()
                    time.sleep(1)  # 요소가 렌더링되는 시간을 충분히 기다림
                else:
                    break
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
                break

        self.driver.quit()

        # 데이터를 CSV 파일로 저장
        current_time = time.strftime("%Y%m%d_%H%M")
        filename = f'faq_{current_time}.csv'
        self.save_to_csv(all_faqs, filename)

        end_time = time.time()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 경과 시간 계산
        print(f"소요 시간: {elapsed_time:.2f}초")


if __name__ == "__main__":
    crawler = AivleCrawler()
    crawler.crawl()
