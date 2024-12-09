import pytest
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

MOODLE_URL = "https://school.moodledemo.net/"
TEACHER_USERNAME = "teacher"
TEACHER_PASSWORD = "moodle2024"  # Replace with the actual default password
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input_editScore.json")
MAX_TIMEOUT = 10
MAX_TIMEOUT_SHORT = 3

@pytest.fixture(scope="class")
def teacher_login():
    driver = webdriver.Chrome()
    driver.set_window_size(926, 804)
    driver.get(MOODLE_URL)
    driver.find_element(By.ID, "lang-menu-toggle").click()
    popup = driver.find_element(By.ID, "lang-menu-toggle")
    element = popup.find_element(By.XPATH, "//*[@id='lang-action-menu']/a[101]")

    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    element.click()
    driver.find_element(By.LINK_TEXT, "Đăng nhập").click()
    driver.find_element(By.ID, "username").send_keys(TEACHER_USERNAME)
    driver.find_element(By.ID, "password").send_keys(TEACHER_PASSWORD)
    driver.find_element(By.ID, "loginbtn").click()
    WebDriverWait(driver, 10).until(
                EC.url_contains("https://school.moodledemo.net/")
            )
    WebDriverWait(driver, MAX_TIMEOUT_SHORT).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Mindful course creation"))
    ).click()
    WebDriverWait(driver, MAX_TIMEOUT_SHORT).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Điểm số"))
    ).click()
    close_modal_if_present(driver)
    driver.find_element(By.XPATH, "//*[@id='usernavigation']/form").click()

    
    # driver.find_element(By.LINK_TEXT, "Điểm số").click()
    # Cuộn đến phần tử và nhấp
    # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    yield driver  # Return the driver for use in tests
    driver.quit()

@pytest.fixture(scope="function")
def precondition(teacher_login):

    driver = teacher_login
    
    
    return driver

first_time = True

def close_modal_if_present(driver):
    global first_time  # Sử dụng biến toàn cục
    if first_time:
        try:
            # Chờ modal xuất hiện
            close_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='tour-step-tool_usertours_13_19_1683276000-0']/div/div/div[4]/button[2]"))
            )
            close_button.click()  # Nhấp để tắt modal
            print("Modal closed on first load.")
        except:
            print("Modal not found on first load.")
        finally:
            first_time = False  # Đặt lại cờ để không kiểm tra lần sau

def load_input_data():
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [
        (
            test["id"],
            test["score"],
            test["error"]
        )
        for test in data
    ]
@pytest.mark.parametrize(
    "id,score,error", load_input_data()
)
@pytest.mark.usefixtures("teacher_login")
class TestEditScore:
    def test_mess(
        self,
        precondition,
        id,
        score,
        error
    ):

        driver = precondition

        elementId = "grade_14_490"
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, elementId))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.send_keys(score)
        driver.find_element(By.ID, "gradersubmit").click()
        
        # element = driver.find_element(By.ID, "id_submitbutton")
        # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        # driver.find_element(By.ID, "id_submitbutton").click()

        time.sleep(3)

        if error is not None:
            # Check for expected error presence
            input_element = driver.find_element(By.ID, elementId)
            validation_message = input_element.get_attribute("validationMessage")
            assert validation_message == ''
        else:
            try:
                value = driver.find_element(By.ID, elementId).get_attribute("value")
                assert value == score
            except NoSuchElementException:
                pytest.fail("Expected error element not found.")
        

