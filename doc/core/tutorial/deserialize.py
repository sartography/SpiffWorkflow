from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.serializer.json import JSONSerializer

serializer = JSONSerializer()
with open('workflow-spec.json') as fp:
    workflow_json = fp.read()
spec = WorkflowSpec.deserialize(serializer, workflow_json)
