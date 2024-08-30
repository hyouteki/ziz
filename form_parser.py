import requests
from lxml import html
import json

debug = True

with open("./tests.json", "r") as file:
    test_urls = json.load(file)["urls"]

class Field:
    def __init__(self, intent, xpath):
        self.intent = intent
        self.xpath = xpath

    def to_dict(self):
        return {"intent": self.intent, "xpath": self.xpath}

class InputField(Field):
    def __init__(self, intent, xpath, type, value):
        super().__init__(intent, xpath)
        self.type = type
        self.value = value

    def to_dict(self):
        field_dict = super().to_dict()
        field_dict.update({"type": self.type, "value": self.value})
        return field_dict
        
class SelectField(Field):
    def __init__(self, intent, xpath, options):
        super().__init__(intent, xpath)
        self.options = options

    def to_dict(self):
        field_dict = super().to_dict()
        field_dict.update({"options": self.options})
        return field_dict
        
class TextareaField(Field):
    def __init__(self, intent, xpath, value):
        super().__init__(intent, xpath)
        self.value = value

    def to_dict(self):
        field_dict = super().to_dict()
        field_dict.update({"value": self.value})
        return field_dict

def find_label(element):
    # Check for preceding sibling label
    if label := element.xpath("preceding-sibling::label[1]"):
        return label[0].text.strip()
    # Check for label with "for" attribute referencing the current element's id
    if element_id := element.get("id"):
        if label := element.xpath(f"//label[@for='{element_id}']"):
            return label[0].text.strip()
    # Return None if no label is found
    return None

def get_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return ""

def extract_field_intent(field):
    if label := find_label(field):
        return label
    return field.get("name")

# Filter out hidden fields or non-meaningful fields
def is_meaningful_field(field):
    non_meaningful_keywords = ["captcha", "honeypot", "hidden"]
    if field.get("type") == "hidden":
        return False
    return not any(
        keyword in field.get("name", "").lower()
        or keyword in field.get("type", "").lower()
        for keyword in non_meaningful_keywords
    )

def foreach_form(form):
    fields = []
    
    for input_field in form.xpath(".//input"):
        if not is_meaningful_field(input_field):
            continue
        field_type = input_field.get("type")
        if field_type == "submit":
            continue  # skip submit button
        field_intent = extract_field_intent(input_field)
        field_value = input_field.get("value")
        field_xpath = input_field.getroottree().getpath(input_field)
        if debug:
            print(f"Input Field: Intent: {field_intent}, XPath: {field_xpath},",
                  f"Type: {field_type}, Value: {field_value}")
        fields.append(InputField(field_intent, field_xpath, field_type, field_value))

    for select_field in form.xpath(".//select"):
        if not is_meaningful_field(select_field):
            continue
        field_intent = extract_field_intent(select_field)
        field_xpath = select_field.getroottree().getpath(select_field)
        field_options = [option.get("value", option.text) for option in select_field.xpath(".//option")]
        if debug:
            print(f"Select Field: Intent: {field_intent}, XPath: {field_xpath}, Options: {field_options}")
        fields.append(SelectField(field_intent, field_xpath, field_options))

    for textarea_field in form.xpath(".//textarea"):
        if not is_meaningful_field(textarea_field):
            continue
        field_intent = extract_field_intent(textarea_field)
        field_xpath = textarea_field.getroottree().getpath(textarea_field)
        field_value = textarea_field.text
        if debug:
            print(f"Textarea Field: Intent: {field_intent}, XPath: {field_xpath}, Value: {field_value}")
        fields.append(TextareaField(field_intent, field_xpath, field_value))

    return fields

def extract_form_fields(url):
    content = get_url_content(url)
    if not content:
        return []
    
    tree = html.fromstring(content)
    forms = tree.xpath("//form")

    fields_dict = []
    for form in forms:
        fields = foreach_form(form)
        if debug:
            print()
        fields_dict.extend([field.to_dict() for field in fields])

    return fields_dict

if __name__ == "__main__":
    output_dict = []
    for url in test_urls:
        print(f"info: processing '{url}'")
        fields_dict = extract_form_fields(url)
        output_dict.append({url: fields_dict})
        
    with open("fields.json", "w") as file:
        json.dump(output_dict, file, indent=4)
