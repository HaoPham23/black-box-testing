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
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.moodle-exception-message'))
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    @pytest.mark.parametrize("file_path,expected_message", load_test_files())
    def test_file_upload(self, file_path, expected_message):
        self.driver.get("https://school.moodledemo.net/")
        self.driver.set_window_size(1296, 696)

        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(
            By.ID, "username").send_keys("amandahamilto205")
        self.driver.find_element(By.ID, "password").send_keys("moodle")
        self.driver.find_element(By.ID, "loginbtn").click()

        self.driver.find_element(By.ID, "user-menu-toggle").click()
        self.driver.find_element(By.LINK_TEXT, "Private files").click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.fp-btn-add > a"))
        ).click()

        time.sleep(3)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        ).send_keys(file_path)

        self.driver.find_element(
            By.CSS_SELECTOR, 'button.fp-upload-btn.btn-primary.btn').click()

        if self.check_error_message_exists():
            error_message = self.driver.find_element(By.CSS_SELECTOR, 'div.moodle-exception-message')
            assert expected_message in error_message.text
            return
        
        if os.path.getsize(file_path) < 90000000:
            time.sleep(15)
        else:
            time.sleep(60*45)
        self.driver.find_element(
            By.CSS_SELECTOR, 'input.btn.btn-primary[name="submitbutton"]').click()

        toast_message = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.toast-message.px-1"))
        )

        assert expected_message in toast_message.text, "Toast message did not appear or text is incorrect"