import json
import requests
from lxml import html

def complete_form(filepath="processed_fields.json", information_path="information.json"):
    with open(filepath, "r") as file:
        form_data = json.load(file)

    with open(information_path, "r") as file:
        information = json.load(file)
    
    for entry in form_data:
        for url, fields in entry.items():
            response = requests.get(url)
            page = html.fromstring(response.content)

            form_data_dict = {}
            
            for field in fields:
                xpath = field["xpath"]
                element = page.xpath(xpath)[0]
                print(f"{element.name} = {information[field['intent']]}")
                form_data_dict[element.name] = information[field["intent"]]

            form_action = page.xpath("//form")[0].action
            if not form_action.startswith("http"):
                form_action = url + form_action

            print(form_action)
            print(form_data_dict)
            response = requests.post(form_action, data=form_data_dict)
            
            print(f"Submitted form at {url}, response status: {response.status_code}")

if __name__ == "__main__":
    complete_form()
