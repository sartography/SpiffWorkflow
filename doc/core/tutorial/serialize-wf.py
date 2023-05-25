import json
from SpiffWorkflow import Workflow
from SpiffWorkflow.serializer.json import JSONSerializer
from nuclear import NuclearStrikeWorkflowSpec

serializer = JSONSerializer()
spec = NuclearStrikeWorkflowSpec()
workflow = Workflow(spec)
data = workflow.serialize(serializer)

# This next line is unnecessary in practice; it just makes the JSON pretty.
pretty = json.dumps(json.loads(data), indent=4, separators=(',', ': '))

open('workflow.json', 'w').write(pretty)
