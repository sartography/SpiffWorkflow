from SpiffWorkflow.exceptions import WorkflowTaskException, SpiffWorkflowException

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

    def _run_hook(self, my_task):
        try:
            my_task.data = DeepMerge.merge(my_task.data, self.dmnEngine.result(my_task))
            super(BusinessRuleTask, self)._run_hook(my_task)
        except SpiffWorkflowException as we:
            we.add_note(f"Business Rule Task '{my_task.task_spec.description}'.")
            raise we
        except Exception as e:
            error = WorkflowTaskException(str(e), task=my_task)
            error.add_note(f"Business Rule Task '{my_task.task_spec.description}'.")
            raise error

