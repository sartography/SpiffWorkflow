from copy import deepcopy

from SpiffWorkflow.exceptions import SpiffWorkflowException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.specs .BpmnSpecMixin import BpmnSpecMixin

class SpiffBpmnTask(BpmnSpecMixin):

    def __init__(self, wf_spec, name, prescript=None, postscript=None, **kwargs):

        # WHy am I doing this instead of just calling super?
        # Because I need to deal with multiple inheritance and the kwargs nightmare created by our parser design
        BpmnSpecMixin.__init__(self, wf_spec, name, **kwargs)
        self.prescript = prescript
        self.postscript = postscript

    @property
    def spec_type(self):
        return 'Spiff BPMN Task'

    def execute_script(self, my_task, script):
        try:
            my_task.workflow.script_engine.execute(my_task, script)
        except Exception as exc:
            my_task._set_state(TaskState.WAITING)
            raise exc

    def get_payload(self, my_task, script, expr):
        try:
            data = deepcopy(my_task.data)
            my_task.worklflow.script_engine.execute(my_task, script, data)
            return my_task.workflow.script_engine._evaluate(expr, data)
        except Exception as exc:
            my_task._set_state(TaskState.WAITING)
            raise exc

    def _update_hook(self, my_task):
        super()._update_hook(my_task)
        if self.prescript is not None:
            try:
                self.execute_script(my_task, self.prescript)
            except SpiffWorkflowException as se:
                se.add_note("Error occurred in the Pre-Script")
                raise se
        return True

    def _on_complete_hook(self, my_task):
        if self.postscript is not None:
            try:
                self.execute_script(my_task, self.postscript)
            except SpiffWorkflowException as se:
                se.add_note("Error occurred in the Post-Script")
                raise se
        super()._on_complete_hook(my_task)
