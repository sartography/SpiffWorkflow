from SpiffWorkflow.serializer.json import JSONSerializer
from strike import NuclearStrike

class NuclearSerializer(JSONSerializer):
    def serialize_nuclear_strike(self, task_spec):
        return self.serialize_task_spec(task_spec)

    def deserialize_nuclear_strike(self, wf_spec, s_state):
        spec = NuclearStrike(wf_spec, s_state['name'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec
