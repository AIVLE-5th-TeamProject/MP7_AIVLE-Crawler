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



class AivleCrawler:
    def __init__(self):
        self.driver_path = config['path']['chrome_driver']
        self.url = config['url']['aivle_url']
        self.output_directory = config['path']['output_directory']
        self.faq_list_selector = config['selector']['faq_list']
        self.category_selector = config['selector']['category']
        self.question_selector = config['selector']['question']
        self.answer_selector = config['selector']['answer']
        self.more_button_selector = config['selector']['more_button']
        self.driver = self.get_chrome_driver()


    def get_chrome_driver(self):
        """ 크롬 드라이버 객체를 생성하는 함수 """
        # Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')               # 크롬 시크릿 모드로 실행
        options.add_argument("--start-maximized")         # 브라우저 창 최대화
        options.add_argument('--disable-gpu')             # GPU 기반/보조 렌더링을 비활성화
        options.add_argument('--no-sandbox')              # 보안 샌드박스 모드 비활성화 : 리눅스에서 루트 사용자로 실행할 때 필요
        options.add_argument('--disable-dev-shm-usage')   # 공유 메모리 제한 해제
        options.add_argument('--disable-cache')           # 캐시 삭제
        options.add_argument('--headless')                # headless 모드로 실행

        # 크롬 브라우저 버전 추적하여 크롬 드라이버 자동 업데이트    
        try:
            # 기존 드라이버로 시도
            service = Service(executable_path=self.driver_path)
            driver = webdriver.Chrome(options=options, service=service)
        except Exception as e:
            print(f"Error using existing driver: {e}")

            # 기존 드라이버 삭제 -> 새 드라이버 설치
            if os.path.exists(self.driver_path):
                os.remove(self.driver_path)
            
            new_driver_path = ChromeDriverManager().install()
            service = Service(executable_path=new_driver_path)
            driver = webdriver.Chrome(options=options, service=service)

        return driver

    def wait_for_element(self, element_type, by_type, identifier, timeout=10):
        """ 웹 페이지에 특정 요소가 완전히 로드될 때까지 대기하는 함수 """
        try:
            wait_element = WebDriverWait(self.driver, timeout)
            # 찾고자 하는 요소가 존재할 때까지 대기
            if element_type == 'locate':
                element = wait_element.until(EC.presence_of_element_located((by_type, identifier)))
                return element
            # 찾고자 하는 요소가 클릭가능할 때까지 대기
            elif element_type == 'click':
                element = wait_element.until(EC.element_to_be_clickable((by_type, identifier)))
                return element
        except TimeoutException:
            return None

    def wait_for_page_load(self, timeout=30):
        """ 페이지 전체가 완전히 로드될 때까지 대기하는 함수 """
        def page_load_condition(d):
            script = "return document.readyState === 'complete'"
            return d.execute_script(script)
        WebDriverWait(self.driver, timeout).until(page_load_condition)

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

    def save_to_csv(self, data):
        """크롤링한 데이터를 CSV 파일로 저장하는 함수"""
        current_time = time.strftime("%Y%m%d_%H%M")
        filename = f'faq_{current_time}.csv'
        filepath = os.path.join(self.output_directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=['category', 'content'])
            writer.writeheader()
            writer.writerows(data)

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
        self.save_to_csv(all_faqs)

        end_time = time.time()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 경과 시간 계산
        print(f"소요 시간: {elapsed_time:.2f}초")


if __name__ == "__main__":
    crawler = AivleCrawler()
    crawler.crawl()
