import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, UnexpectedAlertPresentException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import os
import json

MOODLE_URL = "https://sandbox.moodledemo.net/"
TEACHER_USERNAME = "teacher"
TEACHER_PASSWORD = "sandbox24"
MAX_TIMEOUT_SHORT = 3
MAX_TIMEOUT = 10
MAX_TIMEOUT_LONG = 600
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input.json")

@pytest.fixture(scope="class")
def teacher_login():
    # Initialize a webdriver and log in a teacher
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

def get_input_data():
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [(d["id"], d["courseName"], d["quizName"], d["expected"]) for d in data]

@pytest.mark.usefixtures("teacher_login")
class TestTeacherUploadFile:
    """
    Pre-condition:
        1. "My first course" exists
    """

    @pytest.mark.parametrize("id,courseName,quizName,expected", get_input_data())
    def test_teacher_upload_file(self, id, courseName, quizName, expected):
        """
        Test case:
            Teacher uploads a file to a course
        """
        driver = teacher_login
        # driver.implicitly_wait(MAX_TIMEOUT)
        