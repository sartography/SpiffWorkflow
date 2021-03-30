from SpiffWorkflow.exceptions import WorkflowTaskExecException

from SpiffWorkflow.specs import Simple

from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from box import Box
from ...util.deep_merge import DeepMerge

class BusinessRuleTask(Simple, BpmnSpecMixin):
    """
    Task Spec for a bpmn:businessTask (DMB Decision Reference) node.
    """

    def _on_trigger(self, my_task):
        pass

    def __init__(self, wf_spec, name, dmnEngine=None, **kwargs):
        super().__init__(wf_spec, name, **kwargs)

        self.dmnEngine = dmnEngine
        self.res = None
        self.resDict = None

    def _on_complete_hook(self, my_task):
        try:
            self.res = self.dmnEngine.decide(**my_task.data)
            if self.res is not None:  # it is conceivable that no rules fire.
                self.resDict = self.res.outputAsDict(my_task.data)
                my_task.data = DeepMerge.merge(my_task.data,self.resDict)
            my_task.data = convert.convertFromBox(my_task.data)
            super(BusinessRuleTask, self)._on_complete_hook(my_task)
        except Exception as e:
            raise WorkflowTaskExecException(my_task, str(e))

    def serialize(self, serializer):
        return serializer.serialize_business_rule_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_business_rule_task(wf_spec, s_state)


