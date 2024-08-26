import requests
from bs4 import BeautifulSoup
import json

debug = True
take_only_labels = True

with open("./tests.json", "r") as file:
    test_urls = json.load(file)["urls"]
    
class Field:
    def __init__(self, name, label=None):
        self.name = name
        self.label = label
    def to_dict(self):
        return {"name": self.name, "label": self.label}

class InputField(Field):
    def __init__(self, type, name, value, label=None):
        super().__init__(name, label)
        self.type = type
        self.value = value
    def to_dict(self):
        field_dict = super().to_dict()
        field_dict.update({"type": self.type, "value": self.value})
        return field_dict
        
class SelectField(Field):
    def __init__(self, name, options, label=None):
        super().__init__(name, label)
        self.options = options
    def to_dict(self):
        field_dict = super().to_dict()
        field_dict.update({"options": self.options})
        return field_dict
        
class TextareaField(Field):
    def __init__(self, name, value, label=None):
        super().__init__(name, label)
        self.value = value
    def to_dict(self):
        field_dict = super().to_dict()
        field_dict.update({"value": self.value})
        return field_dict

def find_label(element):
    label = element.find_previous_sibling("label")
    if label and label.text.strip():
        return label.text.strip()
    return None
        
def foreach_form(form):
    fields = []

    for input_field in form.find_all("input"):
        field_type = input_field.get("type")
        if field_type == "submit":
            continue  # skip submit button
        field_name = input_field.get("name")
        field_value = input_field.get("value")
        field_label = find_label(input_field)
        if debug:
            print(f"Input Field: Name: {field_name}, Label: {field_label},",
                  f"Type: {field_type}, Value: {field_value}")
        fields.append(InputField(field_type, field_name, field_value, label=field_label))

    for select_field in form.find_all("select"):
        field_name = select_field.get("name")
        field_options = [option.get("value", option.text) for option in select_field.find_all("option")]
        field_label = find_label(select_field)
        if debug:
            print(f"Select Field: Name: {field_name}, Label: {field_label}, Options: {field_options}")
        fields.append(SelectField(field_name, field_options, label=field_label))

    for textarea_field in form.find_all("textarea"):
        field_name = textarea_field.get("name")
        field_value = textarea_field.text
        field_label = find_label(textarea_field)
        if debug:
            print(f"Textarea Field: Name: {field_name}, Label: {field_label}, Value: {field_value}")
        fields.append(TextareaField(field_name, field_value, field_label))

    return fields

def extract_form_fields(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        forms = soup.find_all("form")

        fields_dict = []
        for i, form in enumerate(forms, 1):
            fields = foreach_form(form)
            if debug:
                print()
            if take_only_labels:
                fields_dict.extend([field.to_dict() for field in fields if field.label != None])
            else:
                fields_dict.extend([field.to_dict() for field in fields])
                
        return fields_dict
                
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return []

if __name__ == "__main__":
    output_dict = []
    for url in test_urls:
        print(f"info: processing '{url}'")
        fields_dict = extract_form_fields(url)
        output_dict.append({url: fields_dict})
        
    with open("fields.json", "w") as file:
        json.dump(output_dict, file, indent=4)
