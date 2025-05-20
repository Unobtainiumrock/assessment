# Form Filler Web Agent

This project demonstrates an automated web agent that navigates to a specified URL and fills out a form using provided mock data, leveraging Selenium for browser automation.

## Features
- Loads mock data from `mock_data.json`
- Uses Selenium and ChromeDriver to fill out a sample form
- Easily extendable for LLM-driven field mapping

## Requirements
- Python 3.8+
- Google Chrome browser

## Installation
1. Clone this repository or download the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or, if using pyproject.toml
   poetry install
   ```

## Usage
1. Ensure `mock_data.json` contains the data you want to use.
2. Run the script:
   ```bash
   python form_filler.py
   ```

The script will open a Chrome browser, navigate to the test form, fill in the fields, and submit the form.

## Project Structure
- `form_filler.py` - Main script for form automation
- `mock_data.json` - Sample data to fill the form
- `pyproject.toml` - Project dependencies and metadata

## Notes
- The script uses `webdriver-manager` to automatically manage ChromeDriver.
- For more robust field mapping, integrate an LLM to analyze the HTML and match data fields dynamically.

## License
MIT 