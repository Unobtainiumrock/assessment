import requests
import json
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add a file handler for persistent logs
file_handler = logging.FileHandler('form_processor.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(file_handler)

TARGET_URL = 'https://mendrika-alma.github.io/form-submission/'
ORIGINAL_HTML = 'original.html'
MOCK_DATA_FILE = 'mock_data.json'
OPENAI_MODEL = "gpt-4o"  # or your preferred model

def download_html(url):
    """Download HTML content from the given URL."""
    try:
        logger.info(f"Downloading HTML from {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Failed to download HTML: {e}")
        raise

def save_html(content, filename):
    """Save HTML content to a file."""
    try:
        logger.info(f"Saving HTML to {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully saved HTML to {filename}")
    except Exception as e:
        logger.error(f"Failed to save HTML: {e}")
        raise

def load_json_data(file_path):
    """Load JSON data from file."""
    try:
        logger.info(f"Loading JSON data from {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info("Successfully loaded JSON data")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON data: {e}")
        raise

def prepare_openai_prompt(html_content, json_data):
    """Prepare the prompt for OpenAI with the HTML and JSON data."""
    prompt = f"""Given this HTML form and JSON data, create a mapping of form fields to JSON values.
The mapping should be in JSON format with the following structure:
{{
    "field_mappings": {{
        "field_id": "json_path_to_value"
    }},
    "checkbox_mappings": {{
        "checkbox_id": "json_path_to_boolean"
    }},
    "select_mappings": {{
        "select_id": "json_path_to_value"
    }}
}}

HTML Form:
{html_content}

JSON Data:
{json.dumps(json_data, indent=2)}

Please analyze the form structure and JSON data, then provide the mapping that would correctly fill the form fields with the corresponding JSON values.
Focus on matching field IDs in the HTML with appropriate values from the JSON structure.
"""
    return prompt

def get_openai_mapping(prompt):
    """Get form field mapping from OpenAI."""
    try:
        logger.info("Requesting mapping from OpenAI")
        logger.debug(f"Using model: {OPENAI_MODEL}")
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        logger.debug("OpenAI client initialized")
        
        # Log the first 500 characters of the prompt to avoid overwhelming logs
        logger.debug(f"Prompt preview: {prompt[:500]}...")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a form processing expert that creates mappings between HTML forms and JSON data. Respond ONLY with the JSON mapping, no other text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Low temperature for more consistent output
        )
        
        # Log the raw response
        logger.debug("Raw OpenAI response received")
        logger.debug(f"Response object type: {type(response)}")
        logger.debug(f"Response content: {response.choices[0].message.content}")
        
        # Extract the mapping from the response
        mapping_text = response.choices[0].message.content
        
        # Try to find JSON content between triple backticks if present
        if "```json" in mapping_text:
            json_content = mapping_text.split("```json")[1].split("```")[0].strip()
        elif "```" in mapping_text:
            json_content = mapping_text.split("```")[1].split("```")[0].strip()
        else:
            json_content = mapping_text.strip()
            
        logger.debug(f"Extracted JSON content: {json_content[:500]}...")
        
        try:
            mapping = json.loads(json_content)
            logger.debug(f"Successfully parsed mapping: {json.dumps(mapping, indent=2)}")
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing failed. Error: {je}")
            logger.error(f"Failed to parse text: {json_content}")
            raise
        
        logger.info("Successfully received and parsed mapping from OpenAI")
        return mapping
        
    except Exception as e:
        logger.error(f"Failed to get mapping from OpenAI: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        raise

def get_nested_value(data, path):
    """Safely get a nested value from a dictionary using a dot-notation path."""
    try:
        # Split the path into parts
        parts = path.split('.')
        # Start with the root data
        current = data
        # Traverse the path
        for part in parts:
            # Handle array access (e.g., entries[0])
            if '[' in part:
                key, index = part.split('[')
                index = int(index.rstrip(']'))
                current = current[key][index]
            else:
                current = current[part]
        return current
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Failed to get value for path {path}: {e}")
        return None

def apply_mapping_to_html(html_content, mapping, json_data):
    """Apply the OpenAI-generated mapping to the HTML content."""
    try:
        logger.info("Applying mapping to HTML")
        
        # Process field mappings
        for field_id, json_path in mapping.get('field_mappings', {}).items():
            try:
                value = get_nested_value(json_data, json_path)
                if value is not None:
                    logger.debug(f"Setting field {field_id} to value: {value}")
                    
                    # Handle textarea elements differently
                    if field_id.startswith('add-info-text'):
                        # Extract the section number from the field ID (e.g., "2" from "add-info-text-2d")
                        section_num = field_id.split('-')[-1][0]  # Get the number before 'd'
                        
                        # Only apply the value if it's for the first entry (section 2)
                        if section_num == '2':
                            # For textareas, we need to set the content between the tags
                            # First, find the textarea element
                            textarea_start = html_content.find(f'<textarea id="{field_id}"')
                            if textarea_start != -1:
                                # Find the closing tag
                                textarea_end = html_content.find('</textarea>', textarea_start)
                                if textarea_end != -1:
                                    # Get the full textarea element
                                    textarea_element = html_content[textarea_start:textarea_end + 11]  # +11 for </textarea>
                                    # Create new textarea with the value
                                    new_textarea = f'<textarea id="{field_id}" name="{field_id}" rows="3" style="width: 100%; border: 1px solid #ccc;">{value}</textarea>'
                                    # Replace the old textarea with the new one
                                    html_content = html_content.replace(textarea_element, new_textarea)
                    else:
                        # For regular input fields
                        html_content = html_content.replace(
                            f'id="{field_id}"',
                            f'id="{field_id}" value="{value}"'
                        )
            except Exception as e:
                logger.error(f"Failed to process field {field_id}: {e}")
                continue
        
        # Process checkbox mappings
        for checkbox_id, json_path in mapping.get('checkbox_mappings', {}).items():
            try:
                # Handle boolean expressions
                if '==' in json_path:
                    path, expected = json_path.split('==')
                    path = path.strip()
                    expected = expected.strip().strip("'").strip('"')
                    value = get_nested_value(json_data, path)
                    is_checked = value == expected
                else:
                    is_checked = bool(get_nested_value(json_data, json_path))
                
                if is_checked:
                    logger.debug(f"Setting checkbox {checkbox_id} to checked")
                    html_content = html_content.replace(
                        f'id="{checkbox_id}"',
                        f'id="{checkbox_id}" checked'
                    )
            except Exception as e:
                logger.error(f"Failed to process checkbox {checkbox_id}: {e}")
                continue
        
        # Process select mappings
        for select_id, json_path in mapping.get('select_mappings', {}).items():
            try:
                value = get_nested_value(json_data, json_path)
                if value is not None:
                    logger.debug(f"Setting select {select_id} to value: {value}")
                    
                    # For select elements, we need to find the option with matching value
                    # First, find the select element
                    select_start = html_content.find(f'<select id="{select_id}"')
                    if select_start != -1:
                        select_end = html_content.find('</select>', select_start)
                        select_content = html_content[select_start:select_end]
                        
                        # Special handling for state fields
                        if select_id in ['state', 'client-state']:
                            # Convert full state name to abbreviation if needed
                            state_abbrev = value
                            if len(value) > 2:  # If it's a full state name
                                # Map full state names to abbreviations
                                state_map = {
                                    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
                                    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
                                    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
                                    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
                                    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
                                    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
                                    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
                                    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
                                    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                                    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
                                    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
                                    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
                                    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
                                }
                                state_abbrev = state_map.get(value, value)
                            
                            # Find the option with matching value
                            option_start = select_content.find(f'<option value="{state_abbrev}">')
                            if option_start != -1:
                                # Add selected attribute to the matching option
                                option_end = select_content.find('</option>', option_start)
                                option = select_content[option_start:option_end]
                                new_option = option.replace('<option', '<option selected')
                                
                                # Replace the original option with the selected one
                                select_content = select_content.replace(option, new_option)
                                
                                # Replace the original select content
                                html_content = html_content.replace(
                                    html_content[select_start:select_end],
                                    select_content
                                )
                        else:
                            # Handle other select elements as before
                            option_start = select_content.find(f'<option value="{value}">')
                            if option_start != -1:
                                # Add selected attribute to the matching option
                                option_end = select_content.find('</option>', option_start)
                                option = select_content[option_start:option_end]
                                new_option = option.replace('<option', '<option selected')
                                
                                # Replace the original option with the selected one
                                select_content = select_content.replace(option, new_option)
                                
                                # Replace the original select content
                                html_content = html_content.replace(
                                    html_content[select_start:select_end],
                                    select_content
                                )
            except Exception as e:
                logger.error(f"Failed to process select {select_id}: {e}")
                continue
        
        logger.info("Successfully applied mapping to HTML")
        return html_content
        
    except Exception as e:
        logger.error(f"Failed to apply mapping to HTML: {e}")
        raise

def main():
    try:
        # Download and save original HTML
        html_content = download_html(TARGET_URL)
        save_html(html_content, ORIGINAL_HTML)
        
        # Load mock data
        mock_data = load_json_data(MOCK_DATA_FILE)
        
        # Get mapping from OpenAI
        prompt = prepare_openai_prompt(html_content, mock_data)
        mapping = get_openai_mapping(prompt)
        
        # Save the mapping for reference
        with open('form_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        logger.info("Saved form mapping to form_mapping.json")
        
        # Apply mapping to HTML
        processed_html = apply_mapping_to_html(html_content, mapping, mock_data)
        
        # Save processed HTML
        output_file = 'processed_form.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_html)
        logger.info(f"Successfully saved processed form to {output_file}")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == '__main__':
    main() 