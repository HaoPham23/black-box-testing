import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, UnexpectedAlertPresentException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import os
import json

MAX_TIMEOUT_SHORT = 3
MAX_TIMEOUT = 10
MAX_TIMEOUT_LONG = 600
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input_changePassword.json")

def get_input_data():
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [(d["id"], d["url"], d["tasks"], d["expected"]) for d in data]

@pytest.mark.parametrize("id, url, tasks, expected", get_input_data())
def test(id, url, tasks, expected):
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    driver.implicitly_wait(MAX_TIMEOUT)
    for task in tasks:
        try:
            wait = WebDriverWait(driver, MAX_TIMEOUT, ignored_exceptions=[StaleElementReferenceException, ElementClickInterceptedException, UnexpectedAlertPresentException, ElementNotInteractableException])
            if task["element_type"] == "link text":
                element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, task["locator"])))
            elif task["element_type"] == "id":
                element = wait.until(EC.presence_of_element_located((By.ID, task["locator"])))
            elif task["element_type"] == "xpath":
                element = wait.until(EC.presence_of_element_located((By.XPATH, task["locator"])))
            elif task["element_type"] == "name":
                element = wait.until(EC.presence_of_element_located((By.NAME, task["locator"])))
            elif task["element_type"] == "css":
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, task["locator"])))
            else: 
                assert task["action"] == "sleep", "Element type not supported"
        except:
            assert "isOptional" in task and task["isOptional"] == "true"

        if task["action"] == "click":
            if element is None: assert False, "Element not found"
            element.click()
        elif task["action"] == "send_keys":
            if element is None: assert False, "Element not found"
            element.send_keys(task["value"])
        elif task["action"] == "clear":
            if element is None: assert False, "Element not found"
            element.clear()
        elif task["action"] == "toggle":
            if element is None: assert False, "Element not found"
            flag = task["value"] == "true"
            if element.is_selected() != flag:
                element.click()
        elif task["action"] == "sleep":
            time.sleep(task["value"])
        else: assert False, "Action not supported"
    
    wait = WebDriverWait(driver, MAX_TIMEOUT)
    try:
        if expected["element_type"] == "link text":
            expect_element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, expected["locator"])))
        elif expected["element_type"] == "id":
            expect_element = wait.until(EC.presence_of_element_located((By.ID, expected["locator"])))
        elif expected["element_type"] == "xpath":
            expect_element = wait.until(EC.presence_of_element_located((By.XPATH, expected["locator"])))
        elif expected["element_type"] == "css":
            expect_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, expected["locator"])))
        
        if expected["action"] == "text":
            assert expect_element.text == expected["value"]
        elif expected["action"] == "is_displayed":
            assert expected["value"] == "true"
    except:
        assert expected["action"] == "is_displayed" and expected["value"] == "false"
    driver.quit()