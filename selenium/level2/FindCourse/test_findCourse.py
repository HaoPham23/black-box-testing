import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By


def load_test_data():
    with open("level2/FindCourse/input_findCourse.json", "r", encoding="utf-8") as f:
        return json.load(f)


class TestFindCourse:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        yield
        self.driver.quit()

    def execute_step(self, step):
        action = step["action"]

        if action == "open":
            self.driver.get(step["url"])
        elif action == "set_window_size":
            self.driver.set_window_size(step["width"], step["height"])
        elif action == "click":
            element = self.driver.find_element(getattr(By, step["elementType"]), step["locator"])
            element.click()
            if step["locator"] in ['loginbtn', "a[data-value='all']"]:
                time.sleep(2)
        elif action == "send_keys":
            element = self.driver.find_element(getattr(By, step["elementType"]), step["locator"])
            element.clear()
            element.send_keys(step["value"])
        elif action == "wait":
            time.sleep(step["seconds"])
        elif action == "validate_courses":
            elements = self.driver.find_elements(By.XPATH, step["locator"])
            actual_courses = [el.text for el in elements]
            expected_courses = step["expected"]
            assert sorted(actual_courses) == sorted(expected_courses), f"Expected: {expected_courses}, Found: {actual_courses}"
        else:
            pytest.fail(f"Unknown action: {action}", pytrace=False)

    @pytest.mark.parametrize("test_case", load_test_data())
    def test_find_course(self, test_case):
        try:
            print(f"Running test case: {test_case['test_case']}")
            for step in test_case["steps"]:
                self.execute_step(step)
        except AssertionError as e:
            pytest.fail(f"Test case '{test_case['test_case']}' FAILED: {str(e)}", pytrace=False)
        finally:
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".avatar").click()
                self.driver.find_element(By.LINK_TEXT, "Thoát").click()
            except Exception as e:
                print("Could not log out properly:", str(e))