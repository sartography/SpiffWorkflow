from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException

from ...specs.Simple import Simple

from ...bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from ...util.deep_merge import DeepMerge


class BusinessRuleTask(Simple, BpmnSpecMixin):
    """
    Task Spec for a bpmn:businessTask (DMB Decision Reference) node.
    """

    def _on_trigger(self, my_task):
        pass

    def __init__(self, wf_spec, name, dmnEngine, **kwargs):
        super().__init__(wf_spec, name, **kwargs)

        self.dmnEngine = dmnEngine
        self.resDict = None

    @property
    def spec_class(self):
        return 'Business Rule Task'

    def _on_complete_hook(self, my_task):
        try:
            my_task.data = DeepMerge.merge(my_task.data,
                                           self.dmnEngine.result(my_task))
            super(BusinessRuleTask, self)._on_complete_hook(my_task)
        except Exception as e:
            raise WorkflowTaskExecException(my_task, str(e))

    def serialize(self, serializer):
        return serializer.serialize_business_rule_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_business_rule_task(wf_spec, s_state)


