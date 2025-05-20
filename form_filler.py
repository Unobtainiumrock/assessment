import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

MOCK_DATA_FILE = 'mock_data.json'
TARGET_URL = 'https://mendrika-alma.github.io/form-submission/'

def load_mock_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def fill_form_field(driver, field_id, value):
    try:
        element = driver.find_element(By.ID, field_id)
        element.clear()
        element.send_keys(value)
        print(f"Filled '{field_id}' with '{value}'")
    except Exception as e:
        print(f"Could not find or fill field '{field_id}': {e}")

def verify_form_fields(driver, mappings):
    print("\nVerifying filled form fields:")
    for field_id in mappings:
        try:
            element = driver.find_element(By.ID, field_id)
            value = element.get_attribute("value")
            print(f"Field '{field_id}': '{value}'")
        except Exception as e:
            print(f"Could not verify field '{field_id}': {e}")

def main():
    data = load_mock_data(MOCK_DATA_FILE)
    client_data = data.get('client', {})
    if not client_data:
        print("No client data found in mock_data.json")
        return
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    try:
        driver.get(TARGET_URL)
        print(f"Navigated to {TARGET_URL}")
        time.sleep(2)
        mappings = {
            'firstName': client_data.get('first_name'),
            'lastName': client_data.get('family_name'),
            'email': client_data.get('email'),
            'phoneNumber': client_data.get('daytime_phone'),
            'address': client_data.get('address_line_1'),
            'city': client_data.get('city'),
            'state': client_data.get('state'),
            'zipCode': client_data.get('zip_code'),
            'country': client_data.get('country'),
            'comments': "This is an automated submission by a web agent."
        }
        for field_id, value in mappings.items():
            if value is not None:
                fill_form_field(driver, field_id, value)
            else:
                print(f"Skipping '{field_id}' as value is not available in mock data.")
        verify_form_fields(driver, mappings)
        driver.save_screenshot("filled_form.png")
        print("Screenshot saved as filled_form.png")
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            print("Form submitted.")
        except Exception as e:
            print(f"Could not find or click submit button: {e}")
        time.sleep(5)
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == '__main__':
    main() 