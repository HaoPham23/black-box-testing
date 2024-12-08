import pytest
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

MOODLE_URL = "https://sandbox.moodledemo.net/"
STUDENT_USERNAME = "student"
STUDENT_PASSWORD = "sandbox24"  # Replace with the actual default password
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input_changePassword.json")
MAX_TIMEOUT = 10
MAX_TIMEOUT_SHORT = 3

@pytest.fixture(scope="class")
def student_login():
    """
    Fixture for logging in as a student and setting up the WebDriver.
    """
    driver = webdriver.Chrome()
    driver.set_window_size(926, 804)
    driver.get(MOODLE_URL)
    driver.find_element(By.ID, "lang-menu-toggle").click()
    driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(103)").click()
    driver.find_element(By.LINK_TEXT, "Đăng nhập").click()
    driver.find_element(By.ID, "username").send_keys(STUDENT_USERNAME)
    driver.find_element(By.ID, "password").send_keys(STUDENT_PASSWORD)
    driver.find_element(By.ID, "loginbtn").click()

    yield driver  # Return the driver for use in tests
    driver.quit()

@pytest.fixture(scope="function")
def precondition(student_login):
    """
    Ensures the precondition of navigating to the password change page.
    """
    driver = student_login
    WebDriverWait(driver, MAX_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "user-menu-toggle"))
    ).click()
    WebDriverWait(driver, MAX_TIMEOUT_SHORT).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Tuỳ chọn"))
    ).click()
    driver.find_element(By.LINK_TEXT, "Đổi mật khẩu").click()
    return driver

def load_input_data():
    """
    Loads test data from the input JSON file.
    """
    with open(INPUT_PATH, "r", encoding='UTF-8') as f:
        data = json.load(f)
    return [
        (
            test["id"],
            test["currentPassword"],
            test["newPassword"],
            test["newPasswordAgain"],
            test["error"]
        )
        for test in data
    ]

def reset_password(driver, current_password, new_password):
    """
    Resets the password to the original state as a postcondition.
    """
    WebDriverWait(driver, MAX_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "user-menu-toggle"))
    ).click()
    WebDriverWait(driver, MAX_TIMEOUT_SHORT).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Tuỳ chọn"))
    ).click()
    driver.find_element(By.LINK_TEXT, "Đổi mật khẩu").click()

    # Fill in the reset password form
    driver.find_element(By.ID, "id_password").send_keys(current_password)
    driver.find_element(By.ID, "id_newpassword1").send_keys(new_password)
    driver.find_element(By.ID, "id_newpassword2").send_keys(new_password)
    driver.find_element(By.ID, "id_submitbutton").click()
    time.sleep(3)

@pytest.mark.parametrize(
    "id,currentPassword,newPassword,newPasswordAgain,error", load_input_data()
)
@pytest.mark.usefixtures("student_login")
class TestChangePassword:
    """
    Class for testing the 'Change Password' feature.
    """

    def test_change_password(
        self,
        precondition,
        id,
        currentPassword,
        newPassword,
        newPasswordAgain,
        error,
    ):
        """
        Test changing password with valid/invalid data.
        """
        driver = precondition

        # Fill in the change password form
        driver.find_element(By.ID, "id_password").send_keys(currentPassword)
        driver.find_element(By.ID, "id_newpassword1").send_keys(newPassword)
        driver.find_element(By.ID, "id_newpassword2").send_keys(newPasswordAgain)
        driver.find_element(By.ID, "id_submitbutton").click()

        time.sleep(3)

        if error is not None:
            # Check for expected error presence
            try:
                assert driver.find_element(By.ID, error).is_displayed()
            except NoSuchElementException:
                pytest.fail("Expected error element not found.")
        else:
            # Ensure no error messages and password change was successful
            assert not driver.find_elements(By.ID, "error")
