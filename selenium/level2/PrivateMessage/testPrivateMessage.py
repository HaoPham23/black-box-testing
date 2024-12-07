# run: pytest testPrivateMessage.py
import json
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time


class TestPrivateMessage:
    with open('messages.json', 'r') as f:
        config = json.load(f)

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.driver = webdriver.Chrome()

        try:
            self.driver.get(self.config['url'])
            self.driver.set_window_size(self.config['window_size']['width'], self.config['window_size']['height'])

            # Login
            self.driver.find_element(By.LINK_TEXT, self.config['selectors']['login_link']['value']).click()
            self.driver.find_element(By.ID, self.config['selectors']['username_input']['value']).send_keys(self.config['login_credentials']['username'])
            self.driver.find_element(By.ID, self.config['selectors']['password_input']['value']).send_keys(self.config['login_credentials']['password'])
            self.driver.find_element(By.ID, self.config['selectors']['login_button']['value']).click()

            # Still login
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(self.config['url'])
            )

            # Open messaging drawer
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, self.config['selectors']['messaging_drawer_toggle']['value'])
                )
            ).click()

            # Navigate to messages
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, self.config['selectors']['messages_overview_toggle']['value'])
                )
            ).click()

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, self.config['selectors']['contact_select']['value'])
                )
            ).click()

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, self.config['selectors']['message_input']['value']))
            ).click()

            yield
        except Exception as e:
            print(f"Setup failed: {e}")
            raise

    def teardown_method(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def send_message(self, message):
        """Send a message in the messaging interface"""
        self.driver.find_element(By.XPATH, self.config['selectors']['message_input']['value']).clear()
        self.driver.find_element(By.XPATH, self.config['selectors']['message_input']['value']).send_keys(message)
        self.driver.find_element(By.CSS_SELECTOR, self.config['selectors']['send_button']['value']).click()
        time.sleep(2)

    def verify_message(self, expected_text):
        """Verify the last sent message matches expected text"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.config['selectors']['message_container']['value']))
            )
            messages = self.driver.find_elements(
                By.XPATH, self.config['selectors']['message_text']['value']
            )

            if not messages:
                raise Exception("No messages found in the container.")

            last_message = messages[-1].text
            print(f"Element found with text: {last_message}")

            assert last_message == expected_text, f"Text does not match! Found: {last_message}"

        except TimeoutException:
            print("Element or container not found within the given time frame.")
            raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise

    @staticmethod
    def load_test_cases():
        with open('messages.json', 'r') as f:
            data = json.load(f)
            return [(case['message'], case['expected_text']) for case in data['test_cases']]

    @pytest.mark.parametrize("message,expected_text", load_test_cases())
    def test_send_message(self, message, expected_text):
        """Test sending various message lengths"""
        print(f"Running test case: Sending '{message}' and expecting '{expected_text}'")
        self.send_message(message)
        self.verify_message(expected_text)