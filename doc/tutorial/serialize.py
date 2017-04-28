import json
from SpiffWorkflow.serializer.json import JSONSerializer
from nuclear import NuclearStrikeWorkflowSpec

serializer = JSONSerializer()
spec = NuclearStrikeWorkflowSpec()
data = spec.serialize(serializer)

# This next line is unnecessary in practice; it just makes the JSON pretty.
pretty = json.dumps(json.loads(data), indent=4, separators=(',', ': '))

open('workflow-spec.json', 'w').write(pretty)
