import json
from SpiffWorkflow.serializer.json import JSONSerializer
from nuclear import NuclearStrikeWorkflowSpec

serializer = JSONSerializer()
spec = NuclearStrikeWorkflowSpec()
data = spec.serialize(serializer)
pretty = json.dumps(data, indent=4, separators=(',', ': '))
open('workflow-spec.json', 'w').write(pretty)
