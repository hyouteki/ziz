import requests
import json
import sys
from termcolor import colored
from lxml import html

debug = True
autofill = False

test_samples_path = "./tests/samples.json"
processed_fields_path = "./data/processed_fields.json"
information_path="./data/information.json"
intent_processed_fields_path = "./data/intent_processed_fields.json"

for arg in sys.argv:
    if arg.startswith("debug="):
        debug = arg[6: ] == "true"
    if arg == "autofill":
        autofill = True

if not autofill:
    from uir_skeleton import SentenceBert_UIR_Model
        
class Log:
    @staticmethod
    def error(message):
        if debug:
            print(colored(f"error: {message}", "red"))

    @staticmethod
    def log(message):
        if debug:
            print(colored(f"log: {message}", "yellow"))

    @staticmethod
    def info(message):
        if debug:
            print(colored(f"info: {message}", "cyan"))

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
            return label[0].text.strip() if label[0].text else None
    # Return None if no label is found
    return None

def get_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        Log.error(e)
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

def parse_foreach_form(form):
    fields = []
    
    for input_field in form.xpath(".//input"):
        if not is_meaningful_field(input_field):
            continue
        field_type = input_field.get("type")
        if field_type == "submit":
            continue  # Skip submit button
        field_intent = extract_field_intent(input_field)
        field_value = input_field.get("value")
        field_xpath = input_field.getroottree().getpath(input_field)
        Log.log(f"Intent='{field_intent}', XPath='{field_xpath}', " +
                f"Type='{field_type}', Value='{field_value}'")
        fields.append(InputField(field_intent, field_xpath, field_type, field_value))

    for select_field in form.xpath(".//select"):
        if not is_meaningful_field(select_field):
            continue
        field_intent = extract_field_intent(select_field)
        field_xpath = select_field.getroottree().getpath(select_field)
        field_options = [option.get("value", option.text)
                         for option in select_field.xpath(".//option")]
        Log.log(f"Intent='{field_intent}', XPath='{field_xpath}', Options='{field_options}'")
        fields.append(SelectField(field_intent, field_xpath, field_options))

    for textarea_field in form.xpath(".//textarea"):
        if not is_meaningful_field(textarea_field):
            continue
        field_intent = extract_field_intent(textarea_field)
        field_xpath = textarea_field.getroottree().getpath(textarea_field)
        field_value = textarea_field.text
        Log.log(f"Intent='{field_intent}', XPath='{field_xpath}', Value='{field_value}'")
        fields.append(TextareaField(field_intent, field_xpath, field_value))

    return fields

def parse_foreach_url(url, html_content=None):
    content = get_url_content(url) if html_content == None else html_content
    if not content:
        error(f"no content found at '{url}'")
        return []
    
    tree = html.fromstring(content)
    forms = tree.xpath("//form")

    fields_dict = []
    for form in forms:
        fields = parse_foreach_form(form)
        fields_dict.extend([field.to_dict() for field in fields])

    return fields_dict

def parse_forms(filepath=test_samples_path, outfilepath=processed_fields_path):
    with open(filepath, "r") as file:
        test_urls = json.load(file)["urls"]

    output_dict = []
    for url in test_urls:
        Log.info(f"processing '{url}'")
        fields_dict = parse_foreach_url(url)
        output_dict.append({url: fields_dict})

    with open(outfilepath, "w") as file:
        json.dump(output_dict, file, indent=4)
        Log.info(f"fields dumped at '{outfilepath}'")

def capture_intent(filepath=processed_fields_path, information_path=information_path,
                   outfilepath=intent_processed_fields_path):
    with open(filepath, "r") as file:
        form_data = json.load(file)
        
    with open(information_path, "r") as file:
        information = json.load(file)
        candidates = list(information.keys())

    Log.info(f"Candidates={candidates}")
    model = SentenceBert_UIR_Model(candidates)
    Log.info(f"Model={model.name()}")

    for entry in form_data:
        for url, fields in entry.items():
            for field in fields:
                intent = model.similarity_score(field["intent"])[0]
                Log.log(f"'{field['intent']}'->'{intent}'")
                field["intent"] = intent

    with open(outfilepath, "w") as file:
        json.dump(form_data, file, indent=4)
        Log.info(f"processed fields dumped at '{outfilepath}'")

def autofill_form(filepath=intent_processed_fields_path, information_path=information_path):
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
                Log.log(f"'{element.name}'='{information[field['intent']]}'")
                form_data_dict[element.name] = information[field["intent"]]

            form_action = page.xpath("//form")[0].action
            if not form_action.startswith("http"):
                form_action = url + form_action

            response = requests.post(form_action, data=form_data_dict)
            
            Log.info(f"form submitted at {url}, response status: {response.status_code}")
        
if __name__ == "__main__":
    if not autofill:
        parse_forms()
        capture_intent()
    autofill_form()        
