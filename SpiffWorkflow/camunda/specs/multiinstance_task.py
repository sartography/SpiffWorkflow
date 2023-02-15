from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.data_spec import TaskDataReference

from SpiffWorkflow.bpmn.specs.MultiInstanceTask import (
    SequentialMultiInstanceTask as BpmnSequentialMITask, 
    ParallelMultiInstanceTask as BpmnParallelMITask,
)

# This is an abomination, but I don't see any other way replicating the older MI functionality

def update_task_spec(my_task):

    task_spec = my_task.task_spec
    if my_task.state != TaskState.WAITING:
        # We have to fix up our state before we can run the parent update, but we still need
        # to inherit our parent data.
        BpmnSpecMixin._update_hook(task_spec, my_task)
        my_task._set_state(TaskState.WAITING)

    if task_spec.cardinality is None:
        # Use the same collection for input and output
        task_spec.data_input = TaskDataReference(task_spec.data_output.name)
        task_spec.input_item = TaskDataReference(task_spec.output_item.name)
    else:
        cardinality = my_task.workflow.script_engine.evaluate(my_task, task_spec.cardinality)
        if not isinstance(cardinality, int):
            # The input data was supplied via "cardinality"
            # We'll use the same reference for input and output item
            task_spec.data_input = TaskDataReference(task_spec.cardinality)
            task_spec.input_item = TaskDataReference(task_spec.output_item.name) if task_spec.output_item is not None else None
            task_spec.cardinality = None
        else:
            # This will be the index
            task_spec.input_item = TaskDataReference(task_spec.output_item.name) if task_spec.output_item is not None else None


class SequentialMultiInstanceTask(BpmnSequentialMITask):

    def _update_hook(self, my_task):
        update_task_spec(my_task)
        return super()._update_hook(my_task)


class ParallelMultiInstanceTask(BpmnParallelMITask):

    def _update_hook(self, my_task):
        if not my_task.internal_data.get('started', False):
            update_task_spec(my_task)
            self.create_children(my_task)
        return super()._update_hook(my_task)