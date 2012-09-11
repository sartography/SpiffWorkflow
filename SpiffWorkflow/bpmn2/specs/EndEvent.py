from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn2.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.Task import Task

__author__ = 'matth'

class EndEvent(ParallelGateway, BpmnSpecMixin):

    def __init__(self, parent, name, is_terminate_event=False, **kwargs):
        super(EndEvent, self).__init__(parent, name, **kwargs)
        self.is_terminate_event = is_terminate_event

    def _on_complete_hook(self, my_task):
        if self.is_terminate_event:
            #Cancel other branches in this workflow:
            for active_task in my_task.workflow.get_tasks(Task.READY | Task.WAITING):
                if active_task.workflow == my_task.workflow:
                    active_task.cancel()
                else:
                    active_task.workflow.cancel()
                    for start_sibling in active_task.workflow.task_tree.children[0].parent.children:
                        if not start_sibling._is_finished():
                            start_sibling.cancel()

            my_task.workflow.refresh_waiting_tasks()

        return super(EndEvent, self)._on_complete_hook(my_task)