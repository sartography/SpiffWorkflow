from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class IntermediateCatchEvent(Simple, BpmnSpecMixin):

    def __init__(self, parent, name, event_spec=None, **kwargs):
        super(IntermediateCatchEvent, self).__init__(parent, name, **kwargs)
        self.event_spec = event_spec

    def _update_state_hook(self, my_task):
        target_state = getattr(my_task, '_bpmn_load_target_state', None)
        if target_state == Task.READY or (not my_task.workflow._is_busy_with_restore() and self.event_spec.has_fired(my_task)):
            super(IntermediateCatchEvent, self)._update_state_hook(my_task)
        else:
            if not my_task.parent._is_finished():
                return
            if not my_task.state == Task.WAITING:
                my_task._set_state(Task.WAITING)
                if not my_task.workflow._is_busy_with_restore():
                    self.entering_waiting_state(my_task)

    def _on_ready_hook(self, my_task):
        self._predict(my_task)

    def accept_message(self, my_task, message):
        if my_task.state == Task.WAITING and self.event_spec._accept_message(my_task, message):
            self._update_state(my_task)
            return True
        return False