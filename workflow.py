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
        
    def to_json(self):
        if self == WorkflowEventType.NewTab:
            return "new_tab"
        elif self == WorkflowEventType.UrlChange:
            return "url_change"
        else:
            raise ValueError(f"error: unknown event type '{self.value}'")

class WorkflowEventTypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, WorkflowEventType):
            return obj.to_json()
        return super().default(obj)
    
class WorkflowEvent:
    def __init__(self, tab_id: int, timestamp: str,
                 event_type: WorkflowEventType,
                 url: str, html: str = None, fields = None) -> "WorkflowEvent":
        self.tab_id = tab_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.url = url
        self.html = html
        self.fields = fields
        if html is not None:
            self.__process_fields()
        
    def __process_fields(self):
        self.fields = parse_foreach_url(self.url, html_content=self.html)
        
    def to_dict(self):
        return {
            "tab_id": self.tab_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "url": self.url,
            "fields": self.fields,
        }

    @classmethod
    def compare(cls, obj1: "WorkflowEvent",
                obj2: "WorkflowEvent") -> (bool, str):
        if obj1.url != obj2.url:
            return (False, "WorkflowEvent urls are different; found "
                    + f"'{obj1.url}' and '{obj2.url}'")
        if len(obj1.fields) != len(obj2.fields):
            return (False, "WorkflowEvent fields count is different; found "
                    + f"'{len(obj1.fields)}' and '{len(obj2.fields)}'")
        for i in range(len(obj1.fields)):
            if obj1.fields[i] != obj2.fields[i]:
                return (False, "WorkflowEvent fields are different; found "
                    + f"'{obj1.fields[i]}' and '{obj2.fields[i]}'")
        return (True, "") 

class Workflow:
    def __init__(self) -> "Workflow":
        self.clear()

    def clear(self):
        self.raw_workflow = None
        self.sequence = []
        
    def from_json(self, workflow_filepath: str = workflow_filepath):
        with open(workflow_filepath, "r") as file:
            self.clear()
            self.raw_workflow = json.load(file)
        for i in range(len(self.raw_workflow["sequence"])):
            seq_ele = self.raw_workflow["sequence"][i]
            seq_ele_html = self.raw_workflow["htmlContent"][i]["html"]
            self.sequence.append(WorkflowEvent(
                seq_ele["tabId"], seq_ele["timestamp"],
                WorkflowEventType.from_str(seq_ele["type"]),
                seq_ele["url"], html=seq_ele_html, fields=None))

    def to_json(self, out_filepath: str = out_filepath):
        with open(out_filepath, "w") as file:
            json.dump([seq_ele.to_dict() for seq_ele in self.sequence],
                      file, indent=4, cls=WorkflowEventTypeEncoder)

    def load_workflow(self, workflow_file: str) -> "Workflow":
        with open(workflow_file, "r") as file:
            self.clear()
            data = json.load(file)
        for ele in data:
            self.sequence.append(WorkflowEvent(
                ele["tab_id"], ele["timestamp"],
                WorkflowEventType.from_str(ele["event_type"]),
                ele["url"], html=None, fields=ele["fields"]))

    @classmethod
    def compare(cls, obj1: "Workflow", obj2: "Workflow") -> (bool, str):
        if len(obj1.sequence) != len(obj2.sequence):
            return (False, "Workflow steps count is different; found "
                    + f"'{len(obj1.sequence)}' and '{len(obj1.sequence)}'")
        for i in range(len(obj1.sequence)):
            is_equal, msg = WorkflowEvent.compare(
                obj1.sequence[i], obj2.sequence[i])
            if not is_equal:
                return (False, msg)
        return (True, "")

if __name__ == "__main__":
    workflow = Workflow()
    # workflow.from_json()
    # workflow.to_json()

    copy_path = "./data/workflow_copy.json"
    # workflow.load_workflow(out_filepath)
    # workflow.to_json(copy_path)

    workflow.load_workflow(out_filepath)
    workflow2 = Workflow()
    workflow2.load_workflow(copy_path)
    print(Workflow.compare(workflow, workflow2))
