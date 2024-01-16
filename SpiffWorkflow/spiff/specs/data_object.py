from SpiffWorkflow.bpmn.specs.data_spec import DataObject as BpmnDataObject

class DataObject(BpmnDataObject):
    def __init__(self, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
