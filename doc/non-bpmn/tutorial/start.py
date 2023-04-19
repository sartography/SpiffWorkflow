from SpiffWorkflow.workflow import Workflow
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.serializer.json import JSONSerializer

# Load from JSON
with open('nuclear.json') as fp:
    workflow_json = fp.read()
serializer = JSONSerializer()
spec = WorkflowSpec.deserialize(serializer, workflow_json)

# Alternatively, create an instance of the Python based specification.
#from nuclear import NuclearStrikeWorkflowSpec
#spec = NuclearStrikeWorkflowSpec()

# Create the workflow.
workflow = Workflow(spec)

# Execute until all tasks are done or require manual intervention.
# For the sake of this tutorial, we ignore the "manual" flag on the
# tasks. In practice, you probably don't want to do that.
workflow.run_all(halt_on_manual=False)

# Alternatively, this is what a UI would do for a manual task.
#workflow.complete_task_from_id(...)
