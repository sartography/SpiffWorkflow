from SpiffWorkflow.storage import JSONSerializer
from strike import NuclearStrike

class NuclearSerializer(JSONSerializer):
    def serialize_nuclear_strike(self, task_spec):
        return self._serialize_task_spec(task_spec)

    def deserialize_nuclear_strike(self, wf_spec, s_state):
        spec = NuclearStrike(wf_spec, s_state['name'], s_state['args'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec
