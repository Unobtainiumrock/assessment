import json
from jinja2 import Environment, FileSystemLoader
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_json_data(file_path):
    """Load JSON data from file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON data: {e}")
        raise

def generate_form_instructions(template_path, json_data):
    """Generate form filling instructions using Jinja2 template."""
    try:
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(template_path)
        
        # Render template with data
        rendered = template.render(data=json_data)
        
        # Parse the rendered JSON
        instructions = json.loads(rendered)
        return instructions
        
    except Exception as e:
        logger.error(f"Failed to generate form instructions: {e}")
        raise

def main():
    try:
        # Load mock data
        data = load_json_data('mock_data.json')
        logger.info("Loaded mock data successfully")
        
        # Generate form instructions
        instructions = generate_form_instructions('form_template.j2', data)
        logger.info("Generated form instructions successfully")
        
        # Save instructions to file
        with open('form_instructions.json', 'w') as f:
            json.dump(instructions, f, indent=2)
        logger.info("Saved form instructions to form_instructions.json")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == '__main__':
    main() 