import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def load_test_data():
    with open("level1/FindCourse/input_findCourse.json", "r") as f:
        return json.load(f)


class TestFindCourse:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.vars = {}
        yield
        self.driver.quit()

    def are_lists_equal(self, list1, list2):
        return sorted(list1) == sorted(list2)

    @pytest.mark.parametrize("test_data", load_test_data())
    def test_fC1(self, test_data):
        search_str = test_data["str"]
        list_course = test_data["list_course"]

        try:
            self.driver.get("https://school.moodledemo.net/?lang=vi")
            self.driver.set_window_size(838, 816)
            element = self.driver.find_element(By.LINK_TEXT, "Đăng nhập")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            self.driver.find_element(By.LINK_TEXT, "Đăng nhập").click()
            self.driver.find_element(By.ID, "username").click()
            self.driver.find_element(By.ID, "username").send_keys("student")
            self.driver.find_element(By.ID, "password").click()
            self.driver.find_element(By.ID, "password").send_keys("moodle2024")
            self.driver.find_element(By.ID, "loginbtn").click()
            time.sleep(2)
            self.driver.find_element(By.ID, "groupingdropdown").click()
            self.driver.find_element(By.CSS_SELECTOR, "a[data-value='all']").click()
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//button[@type='button' and @data-action='limit-toggle']").click()
            self.driver.find_element(By.LINK_TEXT, "Tất cả").click()
            self.driver.find_element(By.CSS_SELECTOR, "input[data-region='input'][data-action='search']").send_keys(search_str)
            time.sleep(5)
            span_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'multiline')]//span[@class='sr-only']")
            span_texts = [span.text for span in span_elements]
            assert self.are_lists_equal(span_texts, list_course), f"Expected: {list_course}, Found: {span_texts}"
        except AssertionError as e:
            pytest.fail(f"Test failed for search='{search_str}': {str(e)}", pytrace=False)
        finally:
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".avatar").click()
                self.driver.find_element(By.LINK_TEXT, "Thoát").click()
            except:
                print("Could not log out properly.")