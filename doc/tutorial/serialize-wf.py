import json
from SpiffWorkflow import Workflow
from SpiffWorkflow.serializer.json import JSONSerializer
from nuclear import NuclearStrikeWorkflowSpec

serializer = JSONSerializer()
spec = NuclearStrikeWorkflowSpec()
workflow = Workflow(spec)
data = workflow.serialize(serializer)
pretty = json.dumps(data, indent=4, separators=(',', ': '))
open('workflow.json', 'w').write(pretty)
