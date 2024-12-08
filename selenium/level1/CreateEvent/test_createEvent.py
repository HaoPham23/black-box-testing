import pytest
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

MOODLE_URL = "https://sandbox.moodledemo.net/"
MOODLE_DASHBOARD_URL = "https://sandbox.moodledemo.net/my/"
MANAGER_USERNAME = "manager"
MANAGER_PASSWORD = "sandbox24"
INPUT_PATH = os.path.join(os.path.dirname(__file__), "input_createEvent.json")
MAX_TIMEOUT = 10
MAX_TIMEOUT_SHORT = 3


@pytest.fixture(scope="class")
def driver_setup():
    """
    Fixture to set up the WebDriver and log in.
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(MOODLE_URL)
    driver.find_element(By.ID, "lang-menu-toggle").click()
    driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(103)").click()
    driver.find_element(By.LINK_TEXT, "Đăng nhập").click()
    driver.find_element(By.ID, "username").send_keys(MANAGER_USERNAME)
    driver.find_element(By.ID, "password").send_keys(MANAGER_PASSWORD)
    driver.find_element(By.ID, "loginbtn").click()

    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def precondition(driver_setup):
    """
    Fixture to navigate to the event creation modal.
    """
    driver = driver_setup
    driver.get(MOODLE_DASHBOARD_URL)
    driver.find_element(By.XPATH, "//button[contains(.,'Sự kiện mới')]").click()
    WebDriverWait(driver, MAX_TIMEOUT).until(
        EC.element_to_be_clickable((By.ID, "id_name"))
    )
    return driver


def load_input_data():
    """
    Loads test data from the input JSON file.
    """
    with open(INPUT_PATH, "r", encoding="UTF-8") as f:
        data = json.load(f)
    return [
        (
            d["id"],
            d["name"],
            d["startDay"],
            d["startMonth"],
            d["startYear"],
            d["startHour"],
            d["startMinute"],
            d["duration"],
            d["endDay"],
            d["endMonth"],
            d["endYear"],
            d["endHour"],
            d["endMinute"],
            d["error"],
        )
        for d in data
    ]

@pytest.mark.usefixtures("precondition")
class TestCreateEvent:
    """
    Test cases for event creation.
    """

    @pytest.mark.parametrize(
        "id,name,startDay,startMonth,startYear,startHour,startMinute,duration,endDay,endMonth,endYear,endHour,endMinute,error",
        load_input_data(),
    )
    def test_create_event(
        self,
        precondition,
        id,
        name,
        startDay,
        startMonth,
        startYear,
        startHour,
        startMinute,
        duration,
        endDay,
        endMonth,
        endYear,
        endHour,
        endMinute,
        error,
    ):
        """
        Tests creating an event.
        """
        driver = precondition

        # Fill in event details
        driver.find_element(By.ID, "id_name").send_keys(name)
        if startDay:
            driver.find_element(By.ID, "id_timestart_day").send_keys(startDay)
        if startMonth:
            driver.find_element(By.ID, "id_timestart_month").send_keys(startMonth)
        if startYear:
            driver.find_element(By.ID, "id_timestart_year").send_keys(startYear)
        if startHour:
            driver.find_element(By.ID, "id_timestart_hour").send_keys(startHour)
        if startMinute:
            driver.find_element(By.ID, "id_timestart_minute").send_keys(startMinute)

        # Expand "Show more..." if needed
        driver.find_element(By.XPATH, "//a[contains(.,'Show more...')]").click()

        if duration:
            if not driver.find_element(By.CSS_SELECTOR, ".form-check-inline:nth-child(9)").is_selected():
                driver.find_element(By.CSS_SELECTOR, ".form-check-inline:nth-child(9)").click()
            driver.find_element(By.ID, "id_timedurationminutes").send_keys(duration)
        else:
            if endDay:
                driver.find_element(By.ID, "id_duration_1").click()
                driver.find_element(By.ID, "id_timedurationuntil_day").send_keys(endDay)
            if endMonth:
                driver.find_element(By.ID, "id_timedurationuntil_month").send_keys(endMonth)
            if endYear:
                driver.find_element(By.ID, "id_timedurationuntil_year").send_keys(endYear)
            if endHour:
                driver.find_element(By.ID, "id_timedurationuntil_hour").send_keys(endHour)
            if endMinute:
                driver.find_element(By.ID, "id_timedurationuntil_minute").send_keys(endMinute)

        WebDriverWait(driver, MAX_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Lưu')]"))
        )
        driver.find_element(By.XPATH, "//button[contains(.,'Lưu')]").click()

        # Check for errors
        if error:
            if error == "moodle-exception-message":
                try:
                    wait = WebDriverWait(driver, MAX_TIMEOUT)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, error)))
                    time.sleep(3)
                    assert driver.find_element(By.CLASS_NAME, error).is_displayed()
                except NoSuchElementException:
                    pytest.fail("Expected error element not found.")
            else:
                try:
                    wait = WebDriverWait(driver, MAX_TIMEOUT)
                    wait.until(EC.presence_of_element_located((By.ID, error)))
                    time.sleep(3)
                    assert driver.find_element(By.ID, error).is_displayed()
                except NoSuchElementException:
                    pytest.fail("Expected error element not found.")
            # error_message = driver.find_element(By.CLASS_NAME, "moodle-exception-message").text
            # assert error in error_message
        else:
            assert True
