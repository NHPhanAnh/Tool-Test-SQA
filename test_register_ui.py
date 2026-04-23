import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    
    driver.quit()

def test_successful_register(driver):
    """Test happy path of the registration functionality."""
    driver.get("http://localhost:3000/auth/register")
    wait = WebDriverWait(driver, 120)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".register-button")))
    except Exception as e:
        driver.save_screenshot("error_screenshot.png")
        print("Page source at failure:\n", driver.page_source[:1000])
        raise e
        
    time.sleep(2) # Wait a bit for Vue reactivity to fully mount
    
    inputs = driver.find_elements(By.TAG_NAME, "input")
    
    # In register.vue, inputs order: FullName, Username, Email, Password, PasswordConfirm
    text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    pass_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
    
    fullname_input = text_inputs[0]
    username_input = text_inputs[1]
    email_input = text_inputs[2]
    
    password_input = pass_inputs[0]
    confirm_input = pass_inputs[1]
    
    # Generate unique user
    uid = random.randint(10000, 99999)
    username = f"sqauser{uid}"
    email = f"{username}@mailinator.com"
    
    fullname_input.send_keys("Test User SQA")
    username_input.send_keys(username)
    email_input.send_keys(email)
    password_input.send_keys("Test@12345")
    confirm_input.send_keys("Test@12345")
    
    time.sleep(1) # wait for Vue validators to update the button state
    
    register_button = driver.find_element(By.CSS_SELECTOR, ".register-button")
    driver.execute_script("arguments[0].click();", register_button)
    
    time.sleep(5) # Wait for API response and UI update
    
    # In CVConnect, after registration it either redirects to /auth/login or shows a .notice for email verification
    current_url = driver.current_url
    is_success = "/auth/login" in current_url or len(driver.find_elements(By.CSS_SELECTOR, ".notice")) > 0
    
    assert is_success, "Registration failed, neither redirected to login nor showed success notice."
    
    # --- ROLLBACK (Teardown) ---
    # Delete the generated test user from the database to clean up the environment
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost",
            port=3307,
            user="root",
            password="123456789",
            database="cvconnect-user-service"
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\\nRollback successful: Deleted test user {username} from database.")
    except Exception as e:
        print(f"\\nRollback failed: {e}")

def test_failed_register_password_mismatch(driver):
    """Test registration failure when passwords do not match."""
    driver.get("http://localhost:3000/auth/register")
    wait = WebDriverWait(driver, 120)
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".register-button")))
    time.sleep(2)
    
    inputs = driver.find_elements(By.TAG_NAME, "input")
    
    text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    pass_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
    
    fullname_input = text_inputs[0]
    username_input = text_inputs[1]
    email_input = text_inputs[2]
    
    password_input = pass_inputs[0]
    confirm_input = pass_inputs[1]
    
    fullname_input.send_keys("Test Mismatch")
    username_input.send_keys("mismatch123")
    email_input.send_keys("mismatch@mailinator.com")
    password_input.send_keys("Test@12345")
    confirm_input.send_keys("WrongPass@999") # Mismatch here
    
    from selenium.webdriver.common.keys import Keys
    confirm_input.send_keys(Keys.TAB) # Trigger blur to run validation
    
    time.sleep(2)
    
    register_button = driver.find_element(By.CSS_SELECTOR, ".register-button")
    
    # Button should be disabled due to form invalidation in Vue
    is_disabled = register_button.get_attribute("disabled") is not None or "disabled" in register_button.get_attribute("class")
    
    assert is_disabled, "Register button should be disabled when passwords do not match."
