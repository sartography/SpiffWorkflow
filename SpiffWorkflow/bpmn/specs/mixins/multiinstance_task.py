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

from copy import deepcopy
from collections.abc import Iterable, Sequence, Mapping, MutableSequence, MutableMapping

from SpiffWorkflow.specs.base import TaskSpec
from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.util.deep_merge import DeepMerge
from SpiffWorkflow.bpmn.specs.bpmn_task_spec import BpmnTaskSpec
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException


class LoopTask(BpmnTaskSpec):

    def _merged_children(self, my_task):
        return my_task.internal_data.get('merged', [])
    
    def _instances(self, my_task):
        return filter(lambda c: c.task_spec.name == self.task_spec, my_task.children)


class StandardLoopTask(LoopTask):

    def __init__(self, wf_spec, bpmn_id, task_spec, maximum, condition, test_before, **kwargs):
        super().__init__(wf_spec, bpmn_id, **kwargs)
        self.task_spec = task_spec
        self.maximum = maximum
        self.condition = condition
        self.test_before = test_before

    def task_info(self, my_task):
        info = super().task_info(my_task)
        info['iterations_completed'] = len(self._merged_children(my_task))
        if self.maximum:
            info['iterations_remaining'] = self.maximum - info['iterations_completed']
        info['instance_map'] = dict((idx, str(t.id)) for idx, t in enumerate(self._instances(my_task)))
        return info

    def _update_hook(self, my_task):
        super()._update_hook(my_task)
        if self.test_before and self.loop_complete(my_task):
            return True
        else:
            my_task._set_state(TaskState.STARTED)
            my_task.internal_data['merged'] = []
            self.create_child(my_task)

    def create_child(self, my_task):
        task_spec = my_task.workflow.spec.task_specs[self.task_spec]
        if not task_spec.completed_event.is_connected(self.merge_child):
            task_spec.completed_event.connect(self.merge_child)
        child = my_task._add_child(task_spec, TaskState.WAITING)
        child.triggered = True
        child.internal_data['iteration'] = len(self._merged_children(my_task))
        child.task_spec._update(child)

    def merge_child(self, workflow, child):
        my_task = child.parent
        DeepMerge.merge(my_task.data, child.data)
        my_task.internal_data['merged'].append(str(child.id))
        if self.loop_complete(my_task):
            my_task._set_state(TaskState.READY)
        else:
            self.create_child(my_task)

    def loop_complete(self, my_task):
        merged = my_task.internal_data.get('merged', [])
        max_complete = self.maximum is not None and len(merged) >= self.maximum
        cond_complete = self.condition is not None and not my_task.workflow.script_engine.evaluate(my_task, self.condition)
        return max_complete or cond_complete


class MultiInstanceTask(LoopTask):

    def __init__(self, wf_spec, bpmn_id, task_spec, cardinality=None, data_input=None,
                 data_output=None, input_item=None, output_item=None, condition=None,
                 **kwargs):

        super().__init__(wf_spec, bpmn_id, **kwargs)
        self.task_spec = task_spec
        self.cardinality = cardinality
        self.data_input = data_input
        self.data_output = data_output
        self.input_item = input_item
        self.output_item = output_item
        self.condition = condition

    def task_info(self, my_task):
        info = super().task_info(my_task)
        info.update({
            'completed': [],
            'running': [],
            'future': my_task.internal_data.get('remaining', []),
            'instance_map': {},
        })
        for task in self._instances(my_task):
            key_or_index = task.internal_data.get('key_or_index')
            value = task.internal_data.get('item') if key_or_index is None else key_or_index
            if task.has_state(TaskState.FINISHED_MASK):
                info['completed'].append(value)
            else:
                info['running'].append(value)
            try:
                info['instance_map'][value] = str(task.id)
            except TypeError:
                info['instance_map'][str(value)] = str(task.id)
        return info

    def merge_child(self, workflow, child):
        """This merges child data into this task's data."""
        my_task = child.parent
        if self.data_output is not None and self.output_item is not None:
            if not self.output_item.exists(child):
                self.raise_data_exception("Expected an output item", child)
            item = self.output_item.get(child)
            key_or_index = child.internal_data.get('key_or_index')
            data_output = self.data_output.get(my_task)
            data_input = self.data_input.get(my_task) if self.data_input is not None else None
            if key_or_index is not None and (isinstance(data_output, Mapping) or data_input is data_output):
                data_output[key_or_index] = item
            else:
                data_output.append(item)
        else:
            DeepMerge.merge(my_task.data, child.data)
        my_task.internal_data['merged'].append(str(child.id))

    def create_child(self, my_task, item, key_or_index=None):

        task_spec = my_task.workflow.spec.task_specs[self.task_spec]
        if not task_spec.completed_event.is_connected(self.merge_child):
            task_spec.completed_event.connect(self.merge_child)
        child = my_task._add_child(task_spec, TaskState.WAITING)
        child.triggered = True
        if self.input_item is not None and self.input_item.exists(my_task):
            raise WorkflowDataException(f'Multiinstance input item {self.input_item.bpmn_id} already exists.', my_task)
        if self.output_item is not None and self.output_item.exists(my_task):
            raise WorkflowDataException(f'Multiinstance output item {self.output_item.bpmn_id} already exists.', my_task)
        if self.input_item is not None:       
            self.input_item.set(child, deepcopy(item))
        if key_or_index is not None:
            child.internal_data['key_or_index'] = key_or_index
        else:
            child.internal_data['item'] = item
        child.task_spec._update(child)

    def check_completion_condition(self, my_task):

        merged = my_task.internal_data.get('merged', [])
        if len(merged) > 0 and self.condition is not None:
            last_child = [c for c in my_task.children if str(c.id) == merged[-1]][0]
            return my_task.workflow.script_engine.evaluate(last_child, self.condition)

    def init_data_output_with_input_data(self, my_task, input_data):

        if not self.data_output.exists(my_task):
            if isinstance(input_data, (MutableMapping, MutableSequence)):
                # We can use the same class if it implements __setitem__
                self.data_output.set(my_task, input_data.__class__())
            elif isinstance(input_data, Mapping):
                # If we have a map without __setitem__, use a dict
                self.data_output.set(my_task, dict())
            else:
                # For all other types, we'll append to a list
                self.data_output.set(my_task, list())
        else:
            output_data = self.data_output.get(my_task)
            if not isinstance(output_data, (MutableSequence, MutableMapping)):
                self.raise_data_exception("Only a mutable map (dict) or sequence (list) can be used for output", my_task)
            if input_data is not output_data and not isinstance(output_data, Mapping) and len(output_data) > 0:
                self.raise_data_exception(
                    "If the input is not being updated in place, the output must be empty or it must be a map (dict)", my_task)

    def init_data_output_with_cardinality(self, my_task):

        if not self.data_output.exists(my_task):
            self.data_output.set(my_task, list())
        else:
            data_output = self.data_output.get(my_task)
            if not isinstance(data_ouput, MutableMapping) and len(data_output) > 0:
                self.raise_data_exception(
                    "If loop cardinality is specificied, the output must be a map (dict) or empty sequence (list)",
                    my_task
                )

    def raise_data_exception(self, message, my_task):
        raise WorkflowDataException(message, my_task, data_input=self.data_input, data_output=self.data_output)


class SequentialMultiInstanceTask(MultiInstanceTask):

    def _update_hook(self, my_task):
        super()._update_hook(my_task)
        my_task.internal_data['merged'] = []
        if self.data_input is not None:
            input_data = self.data_input.get(my_task)
            my_task.internal_data['remaining'] = self.init_remaining_items(my_task)
            if self.data_output is not None:
                self.init_data_output_with_input_data(my_task, input_data)
        else:
            my_task.internal_data['cardinality'] = my_task.workflow.script_engine.evaluate(my_task, self.cardinality)
            my_task.internal_data['current'] = 0
            if self.data_output is not None:
                self.init_data_output_with_cardinality(my_task)
        self.add_next_child(my_task)
        if not self.children_complete(my_task):
            my_task._set_state(TaskState.STARTED)
        else:
            return True

    def task_info(self, my_task):
        info = super().task_info(my_task)
        cardinality = my_task.internal_data.get('cardinality')
        if cardinality is not None:
            info['future'] = [v for v in range(len(info['completed']) + len(info['running']), cardinality)]
        return info

    def add_next_child(self, my_task):
        if self.data_input is not None:
            key_or_index, item = self.get_next_input_item(my_task)
        else:
            key_or_index, item = self.get_next_index(my_task)
        if item is not None:
            self.create_child(my_task, item, key_or_index)

    def get_next_input_item(self, my_task):

        input_data = self.data_input.get(my_task)
        remaining = my_task.internal_data.get('remaining')
        if len(remaining) > 0:
            if isinstance(input_data, (Mapping, Sequence)):
                # In this case, we want to preserve a key or index
                # We definitely need it if the output is a map, or if we're udpating a sequence in place
                key_or_index, item = remaining[0], input_data[remaining[0]]
            else:
                key_or_index, item = None, remaining[0]
            my_task.internal_data['remaining'] = remaining[1:]
            return key_or_index, item
        else:
            return None, None

    def get_next_index(self, my_task):

        current = my_task.internal_data.get('current')
        cardinality = my_task.internal_data.get('cardinality')
        if current < cardinality:
            # If using loop cardinality, use the index as the "item"
            my_task.internal_data['current'] = current + 1
            return None, current
        else:
            return None, None

    def merge_child(self, workflow, child):
        super().merge_child(workflow, child)
        my_task = child.parent
        if self.children_complete(my_task) or self.check_completion_condition(my_task):
            my_task._set_state(TaskState.READY)
        else:
            self.add_next_child(my_task)

    def init_remaining_items(self, my_task):

        if not self.data_input.exists(my_task):
            self.raise_data_exception("Missing data input for multiinstance task", my_task)
        input_data = self.data_input.get(my_task)

        # This is internal bookkeeping, so we know where we are; we get the actual items when we create the task
        if isinstance(input_data, Sequence):
            # For lists, keep track of the index
            remaining = [idx for idx in range(len(input_data))]
        elif isinstance(input_data, Mapping):
            # For dicts, use the keys
            remaining = [key for key in input_data]
        elif isinstance(input_data, Iterable):
            # Otherwise, just copy the objects as a last resort
            remaining = [val for val in input_data]
        else:
            self.raise_data_exception("Multiinstance data input must be iterable", my_task)
        return remaining

    def children_complete(self, my_task):
        if self.data_input is not None:
            return len(my_task.internal_data.get('remaining', [])) == 0
        else:
            return my_task.internal_data.get('current', 0) == my_task.internal_data.get('cardinality', 0)


class ParallelMultiInstanceTask(MultiInstanceTask):

    def _update_hook(self, my_task):
        super()._update_hook(my_task)
        my_task.internal_data['merged'] = []
        self.create_children(my_task)
        # If the input collection or cardinalty is 0, there won't be any children to cause the task to become ready
        if not self.children_complete(my_task):
            my_task._set_state(TaskState.STARTED)
        else:
            return True

    def merge_child(self, workflow, child):
        super().merge_child(workflow, child)
        my_task = child.parent
        if self.check_completion_condition(my_task):
            for child in self._instances(my_task):
                child.cancel()
            my_task._set_state(TaskState.READY)
        elif self.children_complete(my_task):
            my_task._set_state(TaskState.READY)

    def create_children(self, my_task):

        if self.data_input is not None:
            data_input = self.data_input.get(my_task)
            # We have to preserve the key or index for maps/sequences, in case we're updating in place, or the output is a mapping
            if isinstance(data_input, Mapping):
                children = data_input.items()
            elif isinstance(data_input, Sequence):
                children = enumerate(data_input)
            else:
                # We can use other iterables as inputs, but key or index isn't meaningful
                children = ((None, item) for item in data_input)
        else:
            # For tasks specifying the cardinality, use the index as the "item"
            cardinality = my_task.workflow.script_engine.evaluate(my_task, self.cardinality)
            children = ((idx, idx) for idx in range(cardinality))

        if self.data_output is not None:
            if self.data_input is not None:
                self.init_data_output_with_input_data(my_task, self.data_input.get(my_task))
            else:
                self.init_data_output_with_cardinality(my_task)

        for key_or_index, item in children:
            self.create_child(my_task, item, key_or_index)

    def children_complete(self, my_task):
        return all(c.state == TaskState.COMPLETED for c in self._instances(my_task))
