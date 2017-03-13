import json
from SpiffWorkflow import Workflow
from serializer import NuclearSerializer

# Load from JSON
with open('nuclear.json') as fp:
    workflow_json = fp.read()
serializer = NuclearSerializer()
spec = serializer.deserialize_workflow_spec(workflow_json, 'nuclear.json')

# Alternatively, create an instance of the Python based specification.
#from nuclear import NuclearStrikeWorkflowSpec
#spec = NuclearStrikeWorkflowSpec()

# Create the workflow.
workflow = Workflow(spec)

# Execute until all tasks are done or require manual intervention.
workflow.complete_all()

# Alternatively, this is what a UI would do for a manual task.
#workflow.complete_task_from_id(...)
