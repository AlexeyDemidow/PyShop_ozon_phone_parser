import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from selenium_stealth import stealth

import time
import re


class OzonSmartphonesOsSpider(scrapy.Spider):
    name = "ozon_smartphones_os"
    allowed_domains = ["ozon.by"]
    start_urls = ['https://ozon.by/', ]

    def __init__(self):
        self.options = Options()
        self.options.add_argument("--start-maximized")

        self.options.add_argument('--disable-gpu')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=self.options)

        stealth(self.driver,
                languages=["en-US", "en"],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36',
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def parse(self, response):

        links = []
        self.driver.get(response.url)
        original_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="reload-button"]'))).click()
        WebDriverWait(self.driver, 5).until(
            ec.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[1]/div[1]'))).click()
        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="layoutPage"]/div[1]/header/div[2]/div/div/ul/li[2]/a'))).click()
        self.driver.close()
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
            break
        WebDriverWait(self.driver, 5).until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="layoutPage"]/div[1]/div[2]/div[3]/div[2]/div[1]'))).click()
        self.driver.get(self.driver.current_url + f'?sorting=rating')

        for i in range(4):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            try:
                for j in soup.find('div', class_='xi7').find_all('a'):
                    links.append(j['href'])
                WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable(
                    (By.XPATH, '//*[@id="layoutPage"]/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div/a'))).click()
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            except AttributeError:
                WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable(
                    (By.XPATH, '//*[@id="layoutPage"]/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div/a'))).click()
        links = list(set(links))[:100]
        android = []
        ios = []
        for l in links:
            self.driver.get(response.url + l[1:])
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            for r in soup.find_all('dd', class_='uj2'):
                android_match = re.findall('Android [0-9][0-9]', r.text)
                ios_math = re.findall('Apple', r.text)
                if android_match:
                    android.append(*android_match)
                if ios_math:
                    ios.append('iOS 14')

        all = android + ios
        for s in range(len(all)):
            info = {'id': s, 'os': all[s]}
            yield info

