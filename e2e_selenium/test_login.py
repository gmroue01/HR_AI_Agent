from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers import BASE_URL, find_button_by_text, submit_login_form, wait


def _fill(driver, surname, name):
    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Surname']")))
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Surname']").send_keys(surname)
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Name']").send_keys(name)


def test_displays_the_login_form(driver):
    driver.get(BASE_URL)
    heading = wait(driver).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    assert heading.text == "Login"
    assert driver.find_element(By.CSS_SELECTOR, "input[aria-label='Surname']").is_displayed()
    assert driver.find_element(By.CSS_SELECTOR, "input[aria-label='Name']").is_displayed()

    submit = driver.find_element(By.CSS_SELECTOR, "[data-testid='stForm'] button")
    assert submit.is_displayed()
    assert submit.text == "Login"


def test_logs_in_an_employee_with_valid_credentials(driver):
    driver.get(BASE_URL)
    _fill(driver, "Gabriel", "Mroue")
    submit_login_form(driver)

    caption = wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stCaptionContainer']")))
    assert caption.text == "Hello Mroue Gabriel. You are the (employee)"


def test_logs_in_an_hr_user_with_valid_credentials(driver):
    driver.get(BASE_URL)
    _fill(driver, "Lisa", "Bodson")
    submit_login_form(driver)

    caption = wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stCaptionContainer']")))
    assert caption.text == "Hello Bodson Lisa. You are the (HR)"


def test_shows_an_error_for_unknown_credentials(driver):
    driver.get(BASE_URL)
    _fill(driver, "Unknown", "Person")
    submit_login_form(driver)

    alert = wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAlert']")))
    assert alert.text == "No Employee found"
    assert driver.find_element(By.TAG_NAME, "h1").text == "Login"


def test_shows_an_error_when_fields_are_left_empty(driver):
    driver.get(BASE_URL)
    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stForm']")))
    submit_login_form(driver)

    alert = wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAlert']")))
    assert alert.text == "No Employee found"


def test_is_case_sensitive_on_surname_and_name(driver):
    driver.get(BASE_URL)
    _fill(driver, "gabriel", "mroue")
    submit_login_form(driver)

    alert = wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAlert']")))
    assert alert.text == "No Employee found"


def test_allows_logging_out_after_a_successful_login(driver):
    driver.get(BASE_URL)
    _fill(driver, "Gabriel", "Mroue")
    submit_login_form(driver)

    disconnect = wait(driver).until(lambda d: find_button_by_text(d, "Disconnect"))
    assert disconnect.is_displayed()
    disconnect.click()

    wait(driver).until(lambda d: d.find_elements(By.TAG_NAME, "h1") and d.find_elements(By.TAG_NAME, "h1")[0].text == "Login")
