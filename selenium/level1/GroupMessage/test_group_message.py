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

MOODLE_URL = "https://school.moodledemo.net/my/courses.php"
TEACHER_USERNAME = "student"
TEACHER_PASSWORD = "moodle2024"
MAX_TIMEOUT_SHORT = 3
MAX_TIMEOUT = 15
MAX_TIMEOUT_LONG = 600
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input.json")

@pytest.fixture(scope="class")
def student_login():
    # Initialize a webdriver and log in a student
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(MOODLE_URL)
    driver.find_element(By.LINK_TEXT, "Log in").click()
    driver.find_element(By.ID, "username").send_keys(TEACHER_USERNAME)
    driver.find_element(By.ID, "password").send_keys(TEACHER_PASSWORD)
    driver.find_element(By.ID, "loginbtn").click()

    yield driver  # This will return the driver to the test
    # Teardown actions go here
    driver.quit()

@pytest.fixture(scope="function")
def remove_created_message(student_login, **kwargs):
    # Remove previous created quiz (if any)
    driver: webdriver.Chrome = student_login
    driver.implicitly_wait(MAX_TIMEOUT_SHORT)
    yield driver

def get_input_data():
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [(d["id"], d["groupName"], d["messageText"], d["isUserMenu"] == "true", d["expected"]) for d in data]

@pytest.mark.usefixtures("student_login", "remove_created_message")
class TestCreateQuiz:
    """
    Pre-condition:
        1. "My first course" exists
    """

    @pytest.mark.parametrize("id,groupName,messageText,isUserMenu,expected", get_input_data())
    def test_send_group_message(self, remove_created_message, id, groupName, messageText, isUserMenu, expected):
        """
        Test case:
            Student sends a group message
        """
        driver: webdriver.Chrome = remove_created_message
        if '!' == expected[0]: return
        driver.implicitly_wait(MAX_TIMEOUT_SHORT)
        if isUserMenu:
            driver.find_element(By.XPATH, "//a[@id='user-menu-toggle']").click()
            driver.find_element(By.XPATH, "//a[@href='https://school.moodledemo.net/message/index.php']").click()
            time.sleep(2)
            wait = WebDriverWait(driver, MAX_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Group')]"))).click()
            driver.find_element(By.XPATH, f"//strong[contains(text(), '{groupName}')]").click()
            driver.find_element(By.XPATH, "//textarea[@aria-label='Write a message...']").send_keys(messageText)
            driver.find_element(By.XPATH, "//i[@class='icon fa-regular fa-paper-plane fa-fw ']").click()
        else:
            driver.find_element(By.LINK_TEXT, "Home").click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//i[@class='icon fa fa-message fa-fw ']").click()
            wait = WebDriverWait(driver, MAX_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Group')]"))).click()
            driver.find_element(By.XPATH, f"//strong[contains(text(), '{groupName}')]").click()
            driver.find_element(By.XPATH, "//textarea[@aria-label='Write a message...']").send_keys(messageText)
            wait = WebDriverWait(driver, timeout=MAX_TIMEOUT, poll_frequency=0.5, ignored_exceptions=ElementClickInterceptedException)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//i[@class='icon fa-regular fa-paper-plane fa-fw ']"))).click()
        assert driver.find_element(By.XPATH, expected).text == ""