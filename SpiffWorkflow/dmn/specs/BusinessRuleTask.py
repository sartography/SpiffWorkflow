from SpiffWorkflow.exceptions import WorkflowTaskExecException

from SpiffWorkflow.specs import Simple

from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin


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
                my_task.data.update(self.resDict)
            super(BusinessRuleTask, self)._on_complete_hook(my_task)
        except Exception as e:
            raise WorkflowTaskExecException(my_task, str(e))

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_generic(wf_spec, s_state, BusinessRuleTask)
