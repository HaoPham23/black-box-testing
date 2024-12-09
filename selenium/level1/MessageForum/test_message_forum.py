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
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input_messageForum.json")
MAX_TIMEOUT = 10
MAX_TIMEOUT_SHORT = 3

@pytest.fixture(scope="class")
def teacher_login():
    driver = webdriver.Chrome()
    driver.set_window_size(926, 804)
    driver.get(MOODLE_URL)
    driver.find_element(By.ID, "lang-menu-toggle").click()
    popup = driver.find_element(By.ID, "lang-menu-toggle")  # Thay bằng ID của popup nếu có
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
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='module-967']/div/div[2]/div[2]/div/div/a"))
    )
    # Cuộn đến phần tử và nhấp
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    element.click()
    yield driver  # Return the driver for use in tests
    driver.quit()

@pytest.fixture(scope="function")
def precondition(teacher_login):

    driver = teacher_login
    
    
    return driver

def load_input_data():
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [
        (
            test["id"],
            test["subject"],
            test["message"],
            test["error"]
        )
        for test in data
    ]
@pytest.mark.parametrize(
    "id,subject,message,error", load_input_data()
)
@pytest.mark.usefixtures("teacher_login")
class TestMessageForum:
    def test_mess(
        self,
        precondition,
        id,
        subject,
        message,
        error
    ):

        driver = precondition
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='region-main']/div[2]/div[1]/div/div[2]/a"))
        )
        element =driver.find_element (By.XPATH, "//*[@id='region-main']/div[2]/div[1]/div/div[2]/a")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()
        # Fill in the change password form
        element = driver.find_element(By.ID, "id_subject")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        driver.find_element(By.ID, "id_subject").send_keys(subject)

        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='id_message_ifr']"))
        )
        driver.switch_to.frame(iframe)
        editor = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tinymce"))
        )
        editor.send_keys(message)
        driver.switch_to.default_content()
        element = driver.find_element(By.ID, "id_submitbutton")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        driver.find_element(By.ID, "id_submitbutton").click()

        time.sleep(1)

        if error is not None:
            # Check for expected error presence
            try:
                assert driver.find_element(By.ID, error).is_displayed()
            except NoSuchElementException:
                pytest.fail("Expected error element not found.")
            # finally:
            #     try:
            #         driver.find_element(By.CSS_SELECTOR, ".avatar").click()
            #         driver.find_element(By.LINK_TEXT, "Thoát").click()
            #     except:
            #         print("Could not log out properly.")
        else:
            # Ensure no error messages and password change was successful
            assert driver.find_element(By.ID, error).is_displayed()
        

