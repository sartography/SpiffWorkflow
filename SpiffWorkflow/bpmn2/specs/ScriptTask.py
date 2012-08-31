from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class ScriptTask(Simple, BpmnSpecMixin):
    def __init__(self, parent, name, script, **kwargs):
        super(ScriptTask, self).__init__(parent, name, **kwargs)
        self.script = script

    def _on_ready_hook(self, task):
        task.workflow.script_engine.execute(task, self.script)

