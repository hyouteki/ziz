import json
import requests
from lxml import html
from uir_skeleton import SentenceBert_UIR_Model

def capture_intent(filepath="fields.json", information_path="information.json", outfilepath="processed_fields.json"):
    with open(filepath, "r") as file:
        form_data = json.load(file)
        
    with open(information_path, "r") as file:
        information = json.load(file)
        candidates = list(information.keys())

    print(f"info: candidates: {candidates}")
    print()

    model = SentenceBert_UIR_Model(candidates)

    for entry in form_data:
        for url, fields in entry.items():
            for field in fields:
                intent = model.similarity_score(field["intent"])[0]
                print(f"{field['intent']} -> {intent}")
                field["intent"] = intent

    with open(outfilepath, "w") as file:
        json.dump(form_data, file, indent=4)
