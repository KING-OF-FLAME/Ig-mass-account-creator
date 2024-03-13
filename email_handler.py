import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def create_email(username):
    suffix = ''.join(random.choices(string.digits, k=4))
    email_address = f"{username}{suffix}@yopmail.com"
    return email_address

def fetch_otp(driver, email_username):
    # Navigate to Yopmail and fetch the OTP from the inbox
    yopmail_url = f"https://yopmail.com/en/?login={email_username}"
    driver.get(yopmail_url)
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))

    # Extract the OTP from the email body. Update the logic based on how OTP is formatted in the email.
    body_text = driver.find_element(By.TAG_NAME, 'body').text
    otp = re.search(r'\b\d{6}\b', body_text)

    driver.switch_to.default_content()
    
    return otp.group(0) if otp else None
