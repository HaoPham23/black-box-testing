import pytest
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def load_test_data():
    with open("level2/EditStudentName/input_editStudentName.json", "r", encoding="utf-8") as file:
        return json.load(file)


class TestEditStudentName:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.vars = {}
        yield
        self.driver.quit()

    def perform_action(self, action, elementType=None, locator=None, value=None, url=None, width=None, height=None):
        element_types = {
            "ID": By.ID,
            "LINK_TEXT": By.LINK_TEXT,
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "CLASS_NAME": By.CLASS_NAME,
            "TAG_NAME": By.TAG_NAME,
        }

        try:
            if action == "open":
                self.driver.get(url)
            elif action == "set_window_size":
                self.driver.set_window_size(width, height)
            elif action == "click":
                self.driver.find_element(element_types[elementType], locator).click()
                if locator == "id_submitbutton":
                    time.sleep(1)
            elif action == "send_keys":
                self.driver.find_element(element_types[elementType], locator).send_keys(value)
            elif action == "clear":
                self.driver.find_element(element_types[elementType], locator).clear()
            elif action == "assert_text":
                element_text = self.driver.find_element(element_types[elementType], locator).text
                assert element_text == value, f"Expected: {value}, Got: {element_text}"
            else:
                pytest.fail(f"Unknown action: {action}", pytrace=False)
        except Exception as e:
            pytest.fail(f"Action '{action}' failed: {str(e)}", pytrace=False)

    @pytest.mark.parametrize("test_case_data", load_test_data())
    def test_eSN(self, test_case_data):
        try:
            steps = test_case_data["steps"]
            for step in steps:
                action = step["action"]
                elementType = step.get("elementType", None)
                locator = step.get("locator", None)
                value = step.get("value", None)
                url = step.get("url", None)
                width = step.get("width", None)
                height = step.get("height", None)
                self.perform_action(action, elementType, locator, value, url, width, height)

            print(f"Test case '{test_case_data['test_case']}' -> PASS")
        except AssertionError as e:
            pytest.fail(f"Test case '{test_case_data['test_case']}' -> FAIL: {str(e)}", pytrace=False)
        except Exception as e:
            pytest.fail(f"Test case '{test_case_data['test_case']}' -> ERROR: {str(e)}", pytrace=False)
        finally:
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".avatar").click()
                self.driver.find_element(By.LINK_TEXT, "Thoát").click()
            except:
                print("Could not log out properly.")
