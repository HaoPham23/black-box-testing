import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestFindCourse:
    def setup_method(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

    def teardown_method(self):
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
            if (step["locator"] in ['loginbtn', "a[data-value='all']"]):
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
            assert sorted(actual_courses) == sorted(expected_courses)
        else:
            raise ValueError(f"Unknown action: {action}")

    def run_test_case(self, test_case):
        print(f"Running test case: {test_case['test_case']}")
        for step in test_case["steps"]:
            self.execute_step(step)
        print(f"Test case '{test_case['test_case']}' PASSED!")

    def logout(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".avatar").click()
            self.driver.find_element(By.LINK_TEXT, "Thoát").click()
        except Exception as e:
            print("Could not log out properly:", str(e))


if __name__ == "__main__":
    with open("input_findCourse.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    test_instance = TestFindCourse()

    for test_case in test_cases:
        test_instance.setup_method()
        try:
            test_instance.run_test_case(test_case)
        except AssertionError as e:
            print(f"Test case '{test_case['test_case']}' FAILED: {e}")
        finally:
            test_instance.logout()
            test_instance.teardown_method()
