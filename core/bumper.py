#!/usr/bin/env python3
import logging
import pickle
import asyncio

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

_LOGGER = logging.getLogger(__name__)


class Bumper:
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.user = ""
        self.password = ""
        self.forum_link = ""
        self.message = ""
        self.delay = 4
        self.threads = []
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.save_session = False
        self.save_details = False

    def set_login(self, data):
        self.forum_link = data[0]
        self.user = data[1]
        self.password = data[2]
        self.save_session = data[3]

    def set_details(self, data):
        self.threads = data[0].replace(' ', '').split(",")
        self.message = data[1]
        self.delay = data[2]
        self.save_details = data[3]

    def write_cookies(self, path):
        # Writes cookies as binary
        try:
            _LOGGER.info("Attempting to save cookies")
            with open(path, 'wb') as file:
                _LOGGER.info("Successfully loaded")
                pickle.dump(self.driver.get_cookies(), file)
        except Exception:
            _LOGGER.error("Failed to save cookies")
            return

    def read_cookies(self, path):
        # Reads cookies as binary
        try:
            _LOGGER.info("Attempting to fetch cookies")
            with open(path, 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
        except FileNotFoundError:
            _LOGGER.error("Failed to fetch cookies")
            return

    def login(self):
        self.driver.get(f'https://{self.forum_link}/login/')
        user = self.driver.find_element(By.NAME, value="login")
        user.send_keys(self.user)
        password = self.driver.find_element(By.NAME, value="password")
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)
        return len(self.driver.find_elements(By.NAME, value="login")) > 0

    def check_two_step(self):
        return len(self.driver.find_elements(By.NAME, value="code")) > 0

    def two_factor(self, code):
        if len(self.driver.find_elements(By.CLASS_NAME, value="errorOverlay")) > 0:
            self.driver.refresh()
        two_factor_code = self.driver.find_element(By.NAME, value="code")
        two_factor_code.send_keys(code)
        two_factor_code.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 2).until(lambda driver: driver.execute_script("return jQuery.active == 0"))
        return len(self.driver.find_elements(By.CLASS_NAME, value="errorOverlay")) > 0

    async def post(self):
        while True:
            for thread in self.threads:
                self.driver.get(f'https://{self.forum_link}/threads/{thread}')
                self.driver.switch_to.frame(self.driver.find_element(By.TAG_NAME, "iframe"))
                post = self.driver.find_element(By.TAG_NAME, "body")
                post.send_keys(self.message)
                self.driver.switch_to.default_content()
                self.driver.find_element(By.XPATH, "//input[@class='button primary']").click()
            await asyncio.sleep(self.delay * 3600)

    def post_timer(self):
        post = self.loop.create_task(self.post())
        try:
            self.loop.run_until_complete(post)
        except asyncio.CancelledError:
            pass
