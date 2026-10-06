from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://localhost:8501"
WAIT_TIMEOUT = 10
LLM_TIMEOUT = 30


def wait(driver, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout)


def find_button_by_text(driver, text):
    return driver.find_element(By.XPATH, f"//button[.//p[text()='{text}']]")


def fill_login_form(driver, surname, name):
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Surname']").send_keys(surname)
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Name']").send_keys(name)


def submit_login_form(driver):
    driver.find_element(By.CSS_SELECTOR, "[data-testid='stForm'] button").click()


def login(driver, surname, name):
    driver.get(BASE_URL)
    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Surname']")))
    fill_login_form(driver, surname, name)
    submit_login_form(driver)
    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stCaptionContainer']")))
