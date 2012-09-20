from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import Workflow
from SpiffWorkflow.bpmn.BpmnScriptEngine import BpmnScriptEngine

__author__ = 'matth'

class BpmnWorkflow(Workflow):

    def __init__(self, workflow_spec, name=None, script_engine=None, read_only=False, **kwargs):
        super(BpmnWorkflow, self).__init__(workflow_spec, **kwargs)
        self.name = name or workflow_spec.name
        self.script_engine = script_engine or BpmnScriptEngine()
        self._is_busy_with_restore = False
        self.read_only = read_only

    def accept_message(self, message):
        assert not self.read_only
        self.refresh_waiting_tasks()
        self.do_engine_steps()
        for my_task in Task.Iterator(self.task_tree, Task.WAITING):
            my_task.task_spec.accept_message(my_task, message)

    def is_busy_with_restore(self):
        if self.outer_workflow == self:
            return self._is_busy_with_restore
        return self.outer_workflow.is_busy_with_restore()

    def _is_engine_task(self, task_spec):
        return not hasattr(task_spec, 'is_engine_task') or task_spec.is_engine_task()

    def do_engine_steps(self):
        assert not self.read_only
        engine_steps = filter(lambda t: self._is_engine_task(t.task_spec), self.get_tasks(Task.READY))
        while engine_steps:
            for task in engine_steps:
                task.complete()
            engine_steps = filter(lambda t: self._is_engine_task(t.task_spec), self.get_tasks(Task.READY))

    def refresh_waiting_tasks(self):
        assert not self.read_only
        for my_task in self.get_tasks(Task.WAITING):
            my_task.task_spec._update_state(my_task)

    def get_ready_user_tasks(self):
        return filter(lambda t: not self._is_engine_task(t.task_spec), self.get_tasks(Task.READY))

    def get_waiting_tasks(self):
        return self.get_tasks(Task.WAITING)

    def _task_completed_notify(self, task):
        assert (not self.read_only) or self.is_busy_with_restore()
        super(BpmnWorkflow, self)._task_completed_notify(task)

    def _task_cancelled_notify(self, task):
        assert (not self.read_only) or self.is_busy_with_restore()


