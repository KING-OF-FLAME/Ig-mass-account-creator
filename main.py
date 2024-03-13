from account_generator import generate_account_details
from selenium.webdriver.support.select import Select
from email_handler import create_email, fetch_otp
from image_downloader import download_profile_image
from instagram_handler import create_instagram_account
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import logging
import json
import os

def update_temp_db(data):
    with open('db/temp_db.json', 'w') as f:
        json.dump(data, f, indent=4)

def read_temp_db():
    with open('db/temp_db.json', 'r') as f:
        return json.load(f)

# Setting up logging
logging.basicConfig(filename='logs/creation.log', level=logging.INFO, format='%(asctime)s %(message)s')

def main():
  
    # Initialize WebDriver outside and pass to the functions that require it
    service = Service(executable_path=r"D:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    user_details = generate_account_details()
    logging.info(f'Generated user details: {user_details}')

    email_address = create_email(user_details['username'])
    logging.info(f'Created email address: {email_address}')

    # Pass the driver to fetch_otp as well
    otp = fetch_otp(driver, user_details['username'])
    logging.info(f'Fetched OTP: {otp}')

    profile_image_path = download_profile_image()
    logging.info(f'Downloaded profile image: {profile_image_path}')

    # Now pass the driver when calling create_instagram_account
    account_creation_status = create_instagram_account(driver, user_details, email_address, profile_image_path)
    logging.info(f'Account creation status: {account_creation_status}')
   


    # Step 5: Store Temporary Data
    temp_data = {
        'user_details': user_details,
        'email_address': email_address,
        'profile_image_path': profile_image_path,
        'account_creation_status': account_creation_status
    }
    
    update_temp_db(temp_data)
    logging.info('Account creation process completed')

    # Quit the WebDriver
    driver.quit()

if __name__ == '__main__':
    main()
