# Form Processing Automation

This project automates the process of filling out HTML forms using OpenAI's GPT models to generate field mappings between form elements and JSON data.

## Current Workflow

The current implementation follows a three-step process:

1. **HTML Form Download**
   - Downloads the target HTML form from a specified URL
   - Saves a local copy for processing
   - Uses this as the template for form filling

2. **OpenAI Mapping Generation**
   - Sends both the HTML form and JSON data to OpenAI
   - Uses a carefully crafted prompt to generate field mappings
   - Receives structured mapping instructions in JSON format
   - Mapping includes:
     - Regular input fields
     - Checkboxes
     - Select dropdowns
     - Textareas
     - Special handling for state fields and additional info sections

3. **Form Processing**
   - Applies the OpenAI-generated mappings to the HTML
   - Handles special cases like:
     - State name to abbreviation conversion
     - Textarea content placement
     - Section-specific additional info
   - Generates a new HTML file with all fields populated

## Setup

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install Dependencies**
   ```bash
   poetry install
   ```

3. **Environment Setup**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

4. **Run the Processor**
   ```bash
   poetry run python form_processor.py
   ```

## Output Files

**note I left those there for your convenience, but feel free to delete and re-run to generate them again**

- `original.html`: The downloaded form template
- `form_mapping.json`: The OpenAI-generated field mappings
- `processed_form.html`: The final form with all fields populated
- `form_processor.log`: Detailed processing logs

## Future Enhancements

Given more time, I would implement the following improvements:

1. **Selenium Integration**
   - Direct interaction with live web forms
   - Real-time form submission
   - Handling of dynamic content
   - Support for JavaScript-heavy forms

2. **Enhanced Field Mapping**
   - Support for more complex form structures
   - Better handling of nested data
   - Improved validation of field values
   - Support for file uploads

3. **User Interface**
   - Web interface for form processing
   - Real-time preview of form filling
   - Manual override capabilities
   - Batch processing support

4. **Error Handling**
   - More robust error recovery
   - Better validation of OpenAI responses
   - Support for partial form completion
   - Detailed error reporting

5. **Performance Optimization**
   - Caching of form templates
   - Parallel processing of multiple forms
   - Optimized OpenAI prompt engineering
   - Reduced API calls

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 