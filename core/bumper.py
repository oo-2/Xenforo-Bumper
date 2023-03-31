#!/usr/bin/env python3
import logging
import os
import sched, time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager

_LOGGER = logging.getLogger(__name__)


class Bumper:
    def __init__(self):
        self.user = ""
        self.password = ""
        self.forum_link = ""
        self.message = ""
        self.delay = 4
        self.threads = []

        self.loop = sched.scheduler(time.time, time.sleep)

        options = webdriver.ChromeOptions()
        options.add_argument(f'user-data-dir={os.getcwd()}/selenium')
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options,
                                       service=webdriver.chrome.service.Service(ChromeDriverManager().install()))

    def set_website(self, data):
        self.forum_link = data
        self.driver.get(f'https://{self.forum_link}/login/')

    def set_login(self, data):
        self.user = data[0]
        self.password = data[1]

    def update_website(self):
        self.set_details([', '.join(self.threads), self.message, self.delay])

    def set_details(self, data):
        self.threads = data[0].replace(' ', '').split(",")
        self.message = data[1]
        self.delay = data[2]
        if self.forum_link:
            data.append(self.forum_link)
        with open('./resources/details.json', 'w') as f:
            json.dump(data, f)

    def load_details(self):
        with open('./resources/details.json', 'r') as f:
            data = json.load(f)
        self.threads = data[0].replace(' ', '').split(",")
        self.message = data[1]
        self.delay = data[2]
        self.forum_link = data[3]

    def check_login(self):
        self.set_website(self.forum_link)
        return len(self.driver.find_elements(By.NAME, value="login")) > 0

    def check_two_step(self):
        return len(self.driver.find_elements(By.NAME, value="code")) > 0

    def check_duo(self):
        if len(self.driver.find_elements(By.NAME, value="xenduo_passcode")) > 0:
            self.driver.find_elements(By.XPATH, value="//input[@class='button primary']")[1].click()
        return len(self.driver.find_elements(By.NAME, value="xenduo_passcode")) > 0

    def login(self):
        self.driver.get(f'https://{self.forum_link}/login/')
        if len(self.driver.find_elements(By.NAME, value="login")) > 0:
            user = self.driver.find_element(By.NAME, value="login")
            user.send_keys(self.user)
            password = self.driver.find_element(By.NAME, value="password")
            password.send_keys(self.password)
            password.send_keys(Keys.ENTER)
        return len(self.driver.find_elements(By.NAME, value="login")) > 0

    def two_factor(self, code):
        if len(self.driver.find_elements(By.CLASS_NAME, value="errorOverlay")) > 0:
            self.driver.refresh()
        two_factor_code = self.driver.find_element(By.NAME, value="code")
        two_factor_code.send_keys(code)
        two_factor_code.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 2).until(lambda driver: driver.execute_script("return jQuery.active == 0"))
        return len(self.driver.find_elements(By.CLASS_NAME, value="errorOverlay")) > 0

    def post(self):
        _LOGGER.info(f"{len(self.threads)} thread(s) will be bumped...")
        _LOGGER.info(f"Bumping with the message set as:\"{self.message}\"")
        _LOGGER.info(f"Your current delay is set to {self.delay} hour(s)")
        for thread in self.threads:
            _LOGGER.info(f"Bumping thread ID {thread}")
            self.driver.get(f'https://{self.forum_link}/threads/{thread}')
            self.driver.switch_to.frame(self.driver.find_element(By.TAG_NAME, "iframe"))
            post = self.driver.find_element(By.TAG_NAME, "body")
            post.send_keys(self.message)
            self.driver.switch_to.default_content()
            self.driver.find_element(By.XPATH, "//input[@class='button primary']").click()

    def post_timer(self):
        self.load_details()
        self.loop.enter(self.delay * 3600, 1, self.post(), ())
        self.loop.run(False)
