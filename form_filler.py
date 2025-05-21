import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

MOCK_DATA_FILE = 'mock_data.json'
TARGET_URL = 'https://mendrika-alma.github.io/form-submission/'

def load_mock_data(file_path):
    logging.info(f"Loading mock data from {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
    logging.info(f"Loaded mock data: {data}")
    return data

def fill_form_field(driver, field_id, value):
    try:
        logging.info(f"Filling field '{field_id}' with '{value}'")
        element = driver.find_element(By.ID, field_id)
        element.clear()
        element.send_keys(value)
        logging.info(f"Successfully filled '{field_id}'")
    except Exception as e:
        logging.error(f"Could not find or fill field '{field_id}': {e}")

def verify_form_fields(driver, mappings):
    logging.info("Verifying filled form fields:")
    for field_id in mappings:
        try:
            element = driver.find_element(By.ID, field_id)
            value = element.get_attribute("value")
            logging.info(f"Field '{field_id}': '{value}'")
        except Exception as e:
            logging.error(f"Could not verify field '{field_id}': {e}")

def setup_webdriver():
    """Initialize and configure Chrome WebDriver using Selenium's built-in manager."""
    try:
        logger.info("Setting up Chrome WebDriver...")
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Use Selenium's built-in manager
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
        
    except WebDriverException as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during WebDriver setup: {str(e)}")
        raise

def main():
    logging.info("Starting form filling process.")
    try:
        data = load_mock_data(MOCK_DATA_FILE)
    except Exception as e:
        logging.critical(f"Failed to load mock data: {e}")
        return
        
    client_data = data.get('client', {})
    if not client_data:
        logging.error("No client data found in mock_data.json")
        return
        
    try:
        driver = setup_webdriver()
    except Exception as e:
        logging.critical(f"Failed to initialize Chrome WebDriver: {e}")
        return

    try:
        logging.info(f"Navigating to {TARGET_URL}")
        driver.get(TARGET_URL)
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
                logging.warning(f"Skipping '{field_id}' as value is not available in mock data.")
        verify_form_fields(driver, mappings)
        screenshot_path = "filled_form.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot saved as {screenshot_path}")
        try:
            logging.info("Attempting to find and click the submit button...")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            logging.info("Form submitted.")
        except Exception as e:
            logging.error(f"Could not find or click submit button: {e}")
        time.sleep(5)
    except KeyboardInterrupt:
        logging.warning("Script interrupted by user (KeyboardInterrupt). Exiting...")
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
        logging.info("Browser closed.")

if __name__ == '__main__':
    main() 