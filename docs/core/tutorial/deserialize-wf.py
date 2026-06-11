from SpiffWorkflow.workflow import Workflow
from SpiffWorkflow.serializer.json import JSONSerializer

serializer = JSONSerializer()
with open('workflow.json') as fp:
    workflow_json = fp.read()
workflow = Workflow.deserialize(serializer, workflow_json)
