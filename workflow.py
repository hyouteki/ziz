from enum import Enum
from ziz import parse_foreach_url
import json

workflow_filepath = "./data/zizext_workflow_1728564445661.json"
out_filepath = "./data/processed_workflow.json"

class WorkflowEventType(Enum):
    NewTab = 0
    UrlChange = 1
    @classmethod
    def from_str(cls, typ_str: str) -> "WorkflowEventType":
        if typ_str == "new_tab":
            return WorkflowEventType.NewTab
        elif typ_str == "url_change":
            return WorkflowEventType.UrlChange
        else:
            raise ValueError(f"error: unknown event type '{typ_str}'")
        
class WorkflowEvent:
    def __init__(self, tab_id: int, timestamp: str,
                 event_type: WorkflowEventType,
                 url: str, html: str) -> "WorkflowEvent":
        self.tab_id = tab_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.url = url
        self.html = html
        
    def process_fields(self):
        self.fields = parse_foreach_url(self.url, html_content=self.html)
        
    def to_dict(self):
        self.process_fields()
        return {
            "tab_id": self.tab_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "url": self.url,
            "fields": self.fields,
        }
        

class Workflow:
    def __init__(self, workflow_filepath: str =
                 workflow_filepath) -> "Workflow":
        with open(workflow_filepath, "r") as file:
            self.raw_workflow = json.load(file)
            self.sequence = []
        for i in range(len(self.raw_workflow["sequence"])):
            seq_ele = self.raw_workflow["sequence"][i]
            seq_ele_html = self.raw_workflow["htmlContent"][i]["html"]
            self.sequence.append(WorkflowEvent(
                seq_ele["tabId"], seq_ele["timestamp"],
                seq_ele["type"], seq_ele["url"], seq_ele_html))

    def to_json(self, out_filepath: str = out_filepath):
        with open(out_filepath, "w") as file:
            json.dump([seq_ele.to_dict() for seq_ele in self.sequence],
                      file, indent=4)
                        
Workflow().to_json()
