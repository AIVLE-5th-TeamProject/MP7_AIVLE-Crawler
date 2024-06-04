import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from config import config

class BaseCrawler:
    def __init__(self, driver_path, output_directory):
        self.driver_path = driver_path
        self.output_directory = output_directory
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

    def save_to_csv(self, data, filename):
        """크롤링한 데이터를 CSV 파일로 저장하는 함수"""
        filepath = os.path.join(self.output_directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
