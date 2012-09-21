from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class ScriptTask(Simple, BpmnSpecMixin):
    def __init__(self, parent, name, script, **kwargs):
        super(ScriptTask, self).__init__(parent, name, **kwargs)
        self.script = script

    def _on_ready_hook(self, task):
        if task.workflow._is_busy_with_restore():
            return
        assert not task.workflow.read_only
        task.workflow.script_engine.execute(task, self.script)

