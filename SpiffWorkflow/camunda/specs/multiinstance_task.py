# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.specs.mixins import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.data_spec import TaskDataReference

from SpiffWorkflow.bpmn.specs.defaults import (
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
        task_spec.data_input = TaskDataReference(task_spec.data_output.bpmn_id)
        task_spec.input_item = TaskDataReference(task_spec.output_item.bpmn_id)
    else:
        cardinality = my_task.workflow.script_engine.evaluate(my_task, task_spec.cardinality)
        if not isinstance(cardinality, int):
            # The input data was supplied via "cardinality"
            # We'll use the same reference for input and output item
            task_spec.data_input = TaskDataReference(task_spec.cardinality)
            task_spec.input_item = TaskDataReference(task_spec.output_item.bpmn_id) if task_spec.output_item is not None else None
            task_spec.cardinality = None
        else:
            # This will be the index
            task_spec.input_item = TaskDataReference(task_spec.output_item.bpmn_id) if task_spec.output_item is not None else None


class SequentialMultiInstanceTask(BpmnSequentialMITask):

    def _update_hook(self, my_task):
        update_task_spec(my_task)
        return super()._update_hook(my_task)


class ParallelMultiInstanceTask(BpmnParallelMITask):

    def _update_hook(self, my_task):
        update_task_spec(my_task)
        return super()._update_hook(my_task)