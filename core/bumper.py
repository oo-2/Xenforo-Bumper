#!/usr/bin/env python3
import logging
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

_LOGGER = logging.getLogger(__name__)


class Bumper:
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.user = ""
        self.password = ""
        self.two_factor = ""
        self.forum_link = ""
        self.message = ""
        self.delay = 4
        self.threads = []
        self.save_session = False
        self.save_details = False

    def set_login(self, data):
        self.forum_link = data[0]
        self.user = data[1]
        self.password = data[2]
        self.save_session = data[3]

    def set_details(self, data):
        self.threads = data[0]
        self.message = data[1]
        self.delay = data[2]
        self.save_details = data[3]

    def set_two_factor(self, two_factor):
        self.two_factor = two_factor

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

    def start_driver(self):
        self.driver.get(f'https://{self.url}/threads/')


    def post(self):
        self.driver.get(f'https://{self.url}/threads/')


    def login(self):
        user = self.driver.find_element(By.NAME, value="login")
        user.send_keys(self.user)
        password = self.driver.find_element(By.NAME, value="password")
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)
