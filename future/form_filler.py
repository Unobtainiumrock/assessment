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
from form_generator import load_json_data, generate_form_instructions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

MOCK_DATA_FILE = 'mock_data.json'
TARGET_URL = 'https://mendrika-alma.github.io/form-submission/'

def setup_webdriver():
    """Initialize and configure Chrome WebDriver using Selenium's built-in manager."""
    try:
        logger.info("Setting up Chrome WebDriver...")
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.binary_location = "/snap/bin/chromium"
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

def fill_form_field(driver, field_id, value):
    """Fill a form field with the given value."""
    try:
        logger.info(f"Filling field '{field_id}' with '{value}'")
        element = driver.find_element(By.ID, field_id)
        element.clear()
        element.send_keys(value)
        logger.info(f"Successfully filled '{field_id}'")
    except Exception as e:
        logger.error(f"Could not find or fill field '{field_id}': {e}")

def set_checkbox(driver, checkbox_id, should_check):
    """Set a checkbox to the specified state."""
    try:
        logger.info(f"Setting checkbox '{checkbox_id}' to {should_check}")
        checkbox = driver.find_element(By.ID, checkbox_id)
        if checkbox.is_selected() != should_check:
            checkbox.click()
        logger.info(f"Successfully set checkbox '{checkbox_id}'")
    except Exception as e:
        logger.error(f"Could not set checkbox '{checkbox_id}': {e}")

def select_option(driver, select_id, value):
    """Select an option from a dropdown."""
    try:
        logger.info(f"Selecting option '{value}' in '{select_id}'")
        select = driver.find_element(By.ID, select_id)
        select.send_keys(value)
        logger.info(f"Successfully selected option in '{select_id}'")
    except Exception as e:
        logger.error(f"Could not select option in '{select_id}': {e}")

def fill_form_with_instructions(driver, instructions):
    """Fill the form using the generated instructions."""
    try:
        # Fill text fields
        for field_id, value in instructions.get('field_mappings', {}).items():
            if value:
                fill_form_field(driver, field_id, value)

        # Set checkboxes
        for checkbox_id, should_check in instructions.get('checkbox_mappings', {}).items():
            set_checkbox(driver, checkbox_id, should_check)

        # Select dropdown options
        for select_id, value in instructions.get('select_mappings', {}).items():
            if value:
                select_option(driver, select_id, value)

        # Fill client information
        for field_id, value in instructions.get('client_mappings', {}).items():
            if value:
                fill_form_field(driver, field_id, value)

        # Set client checkboxes
        for checkbox_id, should_check in instructions.get('client_checkbox_mappings', {}).items():
            set_checkbox(driver, checkbox_id, should_check)

        # Fill case information
        for field_id, value in instructions.get('case_mappings', {}).items():
            if value:
                fill_form_field(driver, field_id, value)

        # Set case checkboxes
        for checkbox_id, should_check in instructions.get('case_checkbox_mappings', {}).items():
            set_checkbox(driver, checkbox_id, should_check)

        # Fill additional information
        if 'additional_mappings' in instructions:
            for field_id, value in instructions['additional_mappings'].items():
                if value:
                    fill_form_field(driver, field_id, value)

        # Fill signature dates
        for field_id, value in instructions.get('signature_dates', {}).items():
            if value:
                fill_form_field(driver, field_id, value)

    except Exception as e:
        logger.error(f"Error filling form: {e}")
        raise

def main():
    try:
        # Load mock data and generate instructions
        data = load_json_data(MOCK_DATA_FILE)
        instructions = generate_form_instructions('form_template.j2', data)
        logger.info("Generated form instructions successfully")

        # Initialize WebDriver
        driver = setup_webdriver()
        
        try:
            # Navigate to the form
            logger.info(f"Navigating to {TARGET_URL}")
            driver.get(TARGET_URL)
            time.sleep(2)  # Wait for page to load

            # Fill the form
            fill_form_with_instructions(driver, instructions)
            
            # Take screenshot
            screenshot_path = "filled_form.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved as {screenshot_path}")

            # Submit the form
            try:
                logger.info("Attempting to find and click the submit button...")
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                logger.info("Form submitted successfully")
            except Exception as e:
                logger.error(f"Could not submit form: {e}")

            time.sleep(5)  # Wait for submission to complete

        except Exception as e:
            logger.error(f"Error during form filling: {e}")
        finally:
            driver.quit()
            logger.info("Browser closed")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()