import requests
from lxml import html
import json

# Load the JSON data with XPath details
with open("fields.json", "r") as file:
    form_data = json.load(file)

def login_and_get_session(login_url, login_data):
    # Start a session to persist cookies and other session data
    session = requests.Session()
    
    # Fetch the login page
    response = session.get(login_url)
    page = html.fromstring(response.content)

    # Find the login form
    login_form = page.xpath('//form')[0]
    login_action = login_form.action
    if not login_action.startswith("http"):
        login_action = login_url + login_action
    
    # Submit the login form
    response = session.post(login_action, data=login_data)
    return session, response

def fill_and_submit_form(session, form_url, fields):
    # Fetch the page with the form
    response = session.get(form_url)
    page = html.fromstring(response.content)

    # Create a dictionary to store form data
    form_data_dict = {}

    # Iterate through each field in the form
    for field in fields:
        xpath = field.get("xpath")
        field_type = field.get("type")
        element = page.xpath(xpath)[0]

        # Handle input fields (text)
        if field_type == "text":
            value = field.get("value", "")
            form_data_dict[element.name] = value

        # Handle select fields
        elif "options" in field:
            # Choose the appropriate value (example takes first value; modify as needed)
            select_value = field.get("value", field["options"][0])
            form_data_dict[element.name] = select_value

        # Handle textarea fields
        elif field_type == "textarea":
            value = field.get("value", "")
            form_data_dict[element.name] = value

    # Submit the form
    form_action = page.xpath('//form')[0].action
    if not form_action.startswith("http"):
        form_action = form_url + form_action

    response = session.post(form_action, data=form_data_dict)

    # Optionally, print the response or handle it as needed
    print(f"Submitted form at {form_url}, response status: {response.status_code}")
    print(response.text)  # For debugging purposes

if __name__ == "__main__":
    # Example login details
    login_url = "https://dealer.okinawadms.com/"
    login_data = {
        "Uid": "HC28HR",
        "Pwd": "h528hrd"
    }

    # Example URL of the form to fill out
    form_url = "https://dealer.okinawadms.com/"

    # Login and get the session
    session, login_response = login_and_get_session(login_url, login_data)
    
    if login_response.status_code == 200:
        print("Login successful, proceeding to fill the form.")
        for entry in form_data:
            for url, fields in entry.items():
                if url == form_url:
                    fill_and_submit_form(session, url, fields)
    else:
        print("Login failed.")
