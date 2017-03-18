import json
from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import WorkflowSpec
from serializer import NuclearSerializer

# Load from JSON
with open('nuclear.json') as fp:
    workflow_json = fp.read()
serializer = NuclearSerializer()
spec = WorkflowSpec.deserialize(serializer, workflow_json, 'nuclear.json')

# Create the workflow.
workflow = Workflow(spec)
