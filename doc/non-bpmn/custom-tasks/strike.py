from __future__ import print_function
from SpiffWorkflow.specs import Simple

class NuclearStrike(Simple):
    def _on_complete_hook(self, my_task):
        print((self.my_variable, "sent!"))

    def serialize(self, serializer):
        return serializer.serialize_nuclear_strike(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_nuclear_strike(wf_spec, s_state)
