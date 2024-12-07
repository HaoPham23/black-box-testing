# run: pytest testPrivateFileUpload.py
import os
import time
import json
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


class TestFileUpload:
    with open('fileupload.json', 'r') as f:
        config = json.load(f)

    @staticmethod
    def load_test_files():
        with open('fileupload.json', 'r') as f:
            data = json.load(f)
            return [(case['file_path'], case['expected_message']) 
                    for case in data['test_files']]

    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def check_error_message_exists(self):
        try:
            WebDriverWait(self.driver, self.config['timeouts']['error_wait']).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config['selectors']['error_message']))
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    @pytest.mark.parametrize("file_path,expected_message", load_test_files())
    def test_file_upload(self, file_path, expected_message):
        self.driver.get(self.config['url'])
        self.driver.set_window_size(self.config['window_size']['width'], self.config['window_size']['height'])

        self.driver.find_element(By.LINK_TEXT, self.config['selectors']['login_link']).click()
        self.driver.find_element(By.ID, self.config['selectors']['username_field']).send_keys(self.config['credentials']['username'])
        self.driver.find_element(By.ID, self.config['selectors']['password_field']).send_keys(self.config['credentials']['password'])
        self.driver.find_element(By.ID, self.config['selectors']['login_button']).click()

        self.driver.find_element(By.ID, self.config['selectors']['user_menu']).click()
        self.driver.find_element(By.LINK_TEXT, self.config['selectors']['private_files']).click()

        WebDriverWait(self.driver, self.config['timeouts']['element_wait']).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.config['selectors']['add_file_button']))
        ).click()

        time.sleep(3)
        WebDriverWait(self.driver, self.config['timeouts']['element_wait']).until(
            EC.presence_of_element_located((By.XPATH, self.config['selectors']['file_input']))
        ).send_keys(file_path)

        self.driver.find_element(By.CSS_SELECTOR, self.config['selectors']['upload_button']).click()

        if self.check_error_message_exists():
            error_message = self.driver.find_element(By.CSS_SELECTOR, self.config['selectors']['error_message'])
            assert expected_message in error_message.text
            return
        
        if os.path.getsize(file_path) < self.config['file_size_threshold']:
            time.sleep(self.config['timeouts']['small_file_wait'])
        else:
            time.sleep(self.config['timeouts']['large_file_wait'])
        
        self.driver.find_element(By.CSS_SELECTOR, self.config['selectors']['submit_button']).click()

        toast_message = WebDriverWait(self.driver, self.config['timeouts']['element_wait']).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.config['selectors']['toast_message']))
        )

        assert expected_message in toast_message.text, "Toast message did not appear or text is incorrect"