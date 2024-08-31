import json
import requests
from lxml import html

# Load the JSON data
with open("fields.json", "r") as file:
    form_data = json.load(file)

# Iterate through each URL and fill out the forms
for entry in form_data:
    for url, fields in entry.items():
        # Fetch the page content
        response = requests.get(url)
        page = html.fromstring(response.content)

        # Create a dictionary to store form data
        form_data_dict = {}

        # Iterate through each field in the form
        for field in fields:
            xpath = field.get("xpath")
            field_type = field.get("type")
            element = page.xpath(xpath)[0]

            # Handle input fields
            if field_type == "text":
                value = field.get("value", "")
                form_data_dict[element.name] = value

            # Handle select fields
            elif "options" in field:
                # Choose the appropriate value (example takes first value; modify as needed)
                select_value = field.get("value", "in")
                form_data_dict[element.name] = select_value

            # Handle textarea fields
            elif field_type == "textarea":
                value = field.get("value", "")
                form_data_dict[element.name] = value

        # Submit the form
        form_action = page.xpath('//form')[0].action
        if not form_action.startswith("http"):
            form_action = url + form_action

        response = requests.post(form_action, data=form_data_dict)

        # Optionally, print the response or handle it as needed
        print(f"Submitted form at {url}, response status: {response.status_code}")

