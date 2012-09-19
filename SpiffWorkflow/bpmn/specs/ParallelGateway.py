import logging
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Join import Join

LOG = logging.getLogger(__name__)

__author__ = 'matth'

class ParallelGateway(Join, BpmnSpecMixin):

    def _try_fire_unstructured(self, my_task, force=False):
        # Look at the tree to find all places where this task is used.
        tasks = []
        for task in my_task.workflow.get_tasks():
            if task.thread_id != my_task.thread_id:
                continue
            if task.task_spec != my_task.task_spec:
                continue
            if not task._is_finished():
                tasks.append(task)

        # Look up which tasks have a parent that is not already complete.
        waiting_tasks = []
        completed = 0
        for task in tasks:
            if task.parent is None or task.parent._is_finished():
                completed += 1
            else:
                waiting_tasks.append(task)

        return force or len(waiting_tasks) == 0, waiting_tasks

    def _update_state_hook(self, my_task):
        if my_task._is_predicted():
            self._predict(my_task)
        if not my_task.parent._is_finished():
            return

        super(ParallelGateway, self)._update_state_hook(my_task)