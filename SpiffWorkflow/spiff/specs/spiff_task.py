from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.specs .BpmnSpecMixin import BpmnSpecMixin

class SpiffBpmnTask(BpmnSpecMixin):

    def __init__(self, wf_spec, name, lane=None, description=None, prescript=None, postscript=None, **kwargs):

        # WHy am I doing this instead of just calling super?
        # Because I need to deal with multiple inheritance and the kwargs nightmare created by our parser design
        BpmnSpecMixin.__init__(self, wf_spec, name, **kwargs)
        self.prescript = prescript
        self.postscript = postscript

    def execute_script(self, my_task, script):
        try:
            my_task.workflow.script_engine.execute(my_task, script, my_task.data)
        except Exception as exc:
            my_task._setstate(TaskState.WAITING, force=True)
            raise exc

    def _on_ready_hook(self, my_task):
        if self.prescript is not None:
            self.execute_script(my_task, self.prescript)
        super()._on_ready_hook(my_task)

    def _on_complete_hook(self, my_task):
        if self.postscript is not None:
            self.execute_script(my_task, self.postscript)
        super()._on_complete_hook(my_task)