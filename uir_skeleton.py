import time
from abc import ABC, abstractmethod
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

class UIR_Model(ABC):
    def __init__(self, candidates):
        self.candidates = candidates

    @abstractmethod
    def similarity_score(self, test):
        pass

class ZeroShot_UIR_Model(UIR_Model):
    def __init__(self, candidates):
        super().__init__(candidates)
        self.model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
    def similarity_score(self, test):
        result = self.model(test, self.candidates)
        return result["labels"][0], result["scores"][0]

class SentenceBert_UIR_Model(UIR_Model):
    def __init__(self, candidates):
        super().__init__(candidates)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def similarity_score(self, test):
        test_embedding = self.model.encode(test)
        candidate_embeddings = self.model.encode(self.candidates)
        similarity_scores = util.cos_sim(test_embedding, candidate_embeddings)
        best_intent_index = similarity_scores.argmax()
        best_intent = self.candidates[best_intent_index]
        best_score = similarity_scores[0][best_intent_index].item()
        return best_intent, best_score

if __name__ == "__main__":
    candidates = [
        "firstname",
        "middlename",
        "lastname",
        "address",
        "username",
        "customerID",
        "email",
        "pincode",
        "phonenumber"
    ]

    tests = [
        "ctl00$ContentPlaceHolder1$PrtyAdd1",
        "ctl00$ContentPlaceHolder1$PinCode",
        "ctl00$ContentPlaceHolder1$CustPhon1",
        "customername",
        "user name",
        "cust_id",
        "email address",
        "phone",
        "first name",
    ]

    zero_shot_model = ZeroShot_UIR_Model(candidates)
    sentence_bert_model = SentenceBert_UIR_Model(candidates)
    
    while (test := input("Enter field label: ")):
        if test == "quit" or test == "q":
            break
    
    # for test in tests:
        print(f"Field: {test}")
        start_time = time.time()
        result = zero_shot_model.similarity_score(test)
        end_time = time.time()
        print(f"ZeroShot Result: {result[0]}, similarty score: {result[1]}, ",
              f"time taken: {end_time - start_time:.4f}")
        start_time = time.time()
        result = sentence_bert_model.similarity_score(test)
        end_time = time.time()
        print(f"SentenceBert Result: {result[0]}, similarty score: {result[1]}, ",
              f"time taken: {end_time - start_time:.4f}")

