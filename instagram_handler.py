import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import random
import re
import string

# Constants for script execution
SHORT_WAIT = 5
LONG_WAIT = 20
TEMP_DB_PATH = 'temp_db.json'
OTP_INPUT_FIELD = 'confirmationCode'

def slow_typing(element, text):
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.1, 0.3))

def is_username_taken(driver):
    try:
        WebDriverWait(driver, SHORT_WAIT).until(
            EC.visibility_of_element_located((By.XPATH, "//p[contains(text(), 'username is not available')]")))
        return True
    except TimeoutException:
        return False

def fetch_otp_from_yopmail(driver, email_username, max_attempts=5):
    attempt = 0
    otp = None
    yopmail_url = f"https://yopmail.com/en/?login={email_username}&bypass=true"
    
    while attempt < max_attempts and not otp:
        attempt += 1
        print(f"Attempt {attempt} to fetch OTP.")
        driver.get(yopmail_url)
        WebDriverWait(driver, LONG_WAIT).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))
        
        body_text = WebDriverWait(driver, LONG_WAIT).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).text
        print(f"Email body content: {body_text[:500]}")  # Print the first 500 chars of the email content for debugging
        
        otp = re.search(r'\b\d{6}\b', body_text)
        if not otp:
            print("OTP not found, waiting before next attempt.")
            time.sleep(SHORT_WAIT)  # Wait before retrying

    driver.switch_to.default_content()
    
    if not otp:
        raise Exception("OTP not found in the email after several attempts.")
    
    return otp.group(0)

def save_to_temp_db(user_details, email_address, instagram_username, profile_image_path, status):
    data = {
        "user_details": user_details,
        "email_address": email_address,
        "instagram_username": instagram_username,
        "profile_image_path": profile_image_path,
        "account_creation_status": status
    }
    with open(TEMP_DB_PATH, 'w') as f:
        json.dump(data, f)

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')

def create_instagram_account(driver, user_details, email_address, profile_image_path):
    try:
        driver.get('https://www.instagram.com/accounts/emailsignup/')
        WebDriverWait(driver, LONG_WAIT).until(EC.presence_of_element_located((By.NAME, 'emailOrPhone')))

        username_accepted = False
        instagram_username = ""
        while not username_accepted:
            email_input = driver.find_element(By.NAME, 'emailOrPhone')
            email_input.clear()
            slow_typing(email_input, email_address)

            full_name_input = driver.find_element(By.NAME, 'fullName')
            full_name_input.clear()
            slow_typing(full_name_input, user_details['full_name'])

            username_input = driver.find_element(By.NAME, 'username')
            username_input.clear()
            instagram_username = user_details['username'] + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            slow_typing(username_input, instagram_username)

            password_input = driver.find_element(By.NAME, 'password')
            password_input.clear()
            slow_typing(password_input, user_details['password'])
            password_input.send_keys(Keys.ENTER)

            time.sleep(SHORT_WAIT)
            if is_username_taken(driver):
                driver.refresh()
            else:
                username_accepted = True

        # DOB selection
        month_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[title="Month:"]')))
        month_dropdown.click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[title="Month:"] option[value="1"]'))).click()

        day_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[title="Day:"]')))
        day_dropdown.click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[title="Day:"] option[value="1"]'))).click()

        year_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[title="Year:"]')))
        year_dropdown.click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[title="Year:"] option[value="1990"]'))).click()
        
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Next')]")))
        next_button.click()

        # Fetch OTP from Yopmail
        otp = fetch_otp_from_yopmail(driver, email_address.split('@')[0])

        # Input OTP in Instagram
        WebDriverWait(driver, LONG_WAIT).until(
            EC.presence_of_element_located((By.NAME, OTP_INPUT_FIELD)))
        otp_input = driver.find_element(By.NAME, OTP_INPUT_FIELD)
        otp_input.clear()
        slow_typing(otp_input, otp)
        otp_input.send_keys(Keys.ENTER)

        # Verify account creation by checking redirection to the main page
        WebDriverWait(driver, LONG_WAIT).until(EC.url_to_be("https://www.instagram.com/"))
        print("Account successfully created.")
        save_to_temp_db(user_details, email_address, "@" + instagram_username, profile_image_path, "Success")
        return True

    except TimeoutException as te:
        print(f"Timeout occurred: {te}")
        save_to_temp_db(user_details, email_address, "@" + instagram_username, profile_image_path, "Timeout Failure")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        save_to_temp_db(user_details, email_address, "@" + instagram_username, profile_image_path, "Error Failure")
        return False
    finally:
        driver.quit()
