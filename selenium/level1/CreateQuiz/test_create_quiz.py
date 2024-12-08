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

@pytest.fixture(scope="function")
def remove_created_quiz(teacher_login, id, courseName, quizName, **kwargs):
    # Remove previous created quiz (if any)
    driver: webdriver.Chrome = teacher_login
    driver.implicitly_wait(MAX_TIMEOUT_SHORT)
    yield driver
    # try:
    #     wait = WebDriverWait(driver, MAX_TIMEOUT)
    #     activity = wait.until(EC.presence_of_element_located((By.XPATH, f'//div[@data-activityname = "{quizName}"]')))
    #     if activity:
    #         activity.find_element(By.XPATH, '//div[@class = "dropdown"]').click()
    #         activity.find_element(By.LINK_TEXT, "Delete").click()
    #         WebDriverWait(driver, MAX_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '//button[@data-action = "delete"]'))).click()
    # except NoSuchElementException:
    #     pass
    edit_mode = WebDriverWait(driver, MAX_TIMEOUT).until(EC.presence_of_element_located((By.NAME, "setmode")))
    if edit_mode.is_selected() == True:
        edit_mode.click()
    

def get_input_data():
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [(d["id"], d["courseName"], d["quizName"], d["returnButtonText"], d["expected"]) for d in data]

@pytest.mark.usefixtures("teacher_login", "remove_created_quiz")
class TestCreateQuiz:
    """
    Pre-condition:
        1. "My first course" exists
    """

    @pytest.mark.parametrize("id,courseName,quizName,returnButtonText,expected", get_input_data())
    def test_create_quiz(self, remove_created_quiz, id, courseName, quizName, returnButtonText, expected):
        """
        Test case:
            Teacher creates a quiz to a course
        """
        if '!' != expected[0]:
            driver: webdriver.Chrome = remove_created_quiz
            if '!' == expected[0]:
                return
            driver.implicitly_wait(MAX_TIMEOUT_SHORT)
            driver.find_element(By.LINK_TEXT, "My courses").click()
            try:
                WebDriverWait(driver, MAX_TIMEOUT).until(EC.presence_of_element_located((By.LINK_TEXT, courseName))).click()
            except:
                pass # Course is already opened
            edit_mode = WebDriverWait(driver, MAX_TIMEOUT).until(EC.presence_of_element_located((By.NAME, "setmode")))
            if edit_mode.is_selected() == False:
                edit_mode.click()
            try:
                wait = WebDriverWait(driver, timeout=MAX_TIMEOUT, poll_frequency=0.5, ignored_exceptions=ElementClickInterceptedException)
                wait.until(lambda d : d.find_element(By.XPATH, "//span[contains(.,'Add an activity or resource')]").click() or True)
            except ElementNotInteractableException: return

            WebDriverWait(driver, MAX_TIMEOUT).until(EC.presence_of_element_located((By.LINK_TEXT, "Quiz"))).click()
            quiz_name = driver.find_element(By.XPATH, '//*[@id="id_name"]')
            quiz_name.clear()
            quiz_name.send_keys(quizName)
            driver.find_element(By.XPATH, f'//input[@value="{returnButtonText}"]').click()
            wait = WebDriverWait(driver, MAX_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.XPATH, expected)) or True)
            assert driver.find_element(By.XPATH, expected).is_displayed()
            # driver.implicitly_wait(MAX_TIMEOUT)
        else:
            driver: webdriver.Chrome = remove_created_quiz
            wait = WebDriverWait(driver, timeout=MAX_TIMEOUT, poll_frequency=0.5, ignored_exceptions=ElementClickInterceptedException)
            wait.until(lambda d : d.find_element(By.LINK_TEXT, "My courses").click() or True)
            try:
                WebDriverWait(driver, MAX_TIMEOUT).until(EC.presence_of_element_located((By.LINK_TEXT, courseName))).click()
            except:
                pass # Course is already opened
            try:
                driver.find_element(By.XPATH, expected[1:])
                is_displayed = True
            except NoSuchElementException:
                is_displayed = False
            assert is_displayed == False