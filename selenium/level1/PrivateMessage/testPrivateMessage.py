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
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.driver = webdriver.Chrome()

        try:
            self.driver.get("https://school.moodledemo.net/")
            self.driver.set_window_size(1296, 696)

            # Login
            self.driver.find_element(By.LINK_TEXT, "Log in").click()
            self.driver.find_element(
                By.ID, "username").send_keys("amandahamilto205")
            self.driver.find_element(By.ID, "password").send_keys("moodle")
            self.driver.find_element(By.ID, "loginbtn").click()

            # Still login
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("https://school.moodledemo.net/")
            )

            # Open messaging drawer
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[@aria-label='Toggle messaging drawer']")
                )
            ).click()

            # Navigate to messages
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#view-overview-messages-toggle .font-weight-bold")
                )
            ).click()

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".w-100:nth-child(2) > .m-0"))
            ).click()

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//textarea[@aria-label='Write a message...']"))
            ).click()

            yield
        except Exception as e:
            print(f"Setup failed: {e}")
            raise

    def teardown_method(self):
        # Clean up (close the browser) after all tests
        if hasattr(self, 'driver'):
            self.driver.quit()

    def send_message(self, message):
        """Send a message in the messaging interface"""
        self.driver.find_element(
            By.XPATH, "//textarea[@aria-label='Write a message...']").clear()
        self.driver.find_element(
            By.XPATH, "//textarea[@aria-label='Write a message...']").send_keys(message)
        self.driver.find_element(By.CSS_SELECTOR, ".mt-auto").click()
        time.sleep(2)

    def verify_message(self, expected_text):
        """Verify the last sent message matches expected text"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[data-region="content-message-container"]'))
            )
            messages = self.driver.find_elements(
                By.XPATH, "//div[@data-region='content-message-container']//div[@dir='auto' and @align='initial' and @data-region='text-container']/p"
            )

            if not messages:
                raise Exception("No messages found in the container.")

            last_message = messages[-1].text
            print(f"Element found with text: {last_message}")

            # Assert message matches expected text
            assert last_message == expected_text, f"Text does not match! Found: {
                last_message}"

        except TimeoutException:
            print("Element or container not found within the given time frame.")
            raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise

    def load_test_cases():
        with open('messages.json', 'r') as f:
            data = json.load(f)
            return [(case['message'], case['expected_text']) for case in data['test_cases']]

    @pytest.mark.parametrize("message,expected_text", load_test_cases())

    def test_send_message(self, message, expected_text):
        """Test sending various message lengths"""
        print(f"Running test case: Sending '{
              message}' and expecting '{expected_text}'")
        self.send_message(message)
        self.verify_message(expected_text)
