import cohere
import json

with open("COHERE_API_KEY", "r") as file:
    COHERE_API_KEY = file.readline()

cohere_client = cohere.Client(COHERE_API_KEY)

with open("information.json", "r") as file:
    user_data = json.load(file)

def generate_response(prompt):
    response = cohere_client.generate(
        model="command-xlarge",
        prompt=prompt,
        max_tokens=150
    )
    return response.generations[0].text.strip()

def get_user_info(query):
    return generate_response(f"""
    You have the following user data:
    {user_data}
    
    The user asked: "{query}"
    
    Please provide only the answer, without any extra description.
    """)

queries = [
    "What is the name?",
    "Give me the user's name",
    "What is the full name?",
    "customername",
    "customerID",
    "What is the email address?",
    "Where does the user live?"
]

for query in queries:
    print(f"Query: {query}")
    print(f"Response: {get_user_info(query)}\n")
