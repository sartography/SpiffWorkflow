# -*- coding: utf-8 -*-

# Copyright (C) 2020 Sartography
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
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

from ...task import TaskState
from ...util.deep_merge import DeepMerge
from ..exceptions import WorkflowDataException
from .BpmnSpecMixin import BpmnSpecMixin


class LoopTask(BpmnSpecMixin):

    def process_children(self, my_task):
        """
        Handle any newly completed children and update merged tasks. 
        Returns a boolean indicating whether there is a child currently running
        """
        merged = my_task.internal_data.get('merged') or []
        child_running = False
        for child in my_task.children:
            if child.task_spec == self.task_spec and child._has_state(TaskState.FINISHED_MASK) and str(child.id) not in merged:
                self.child_completed_action(my_task, child)
                merged.append(str(child.id))
            elif child.task_spec == self.task_spec and not child._has_state(TaskState.FINISHED_MASK):
                child_running = True
        my_task.internal_data['merged'] = merged
        return child_running    

    def child_completed_action(self, my_task, child):
        raise NotImplementedError


class StandardLoopTask(LoopTask):

    def __init__(self, wf_spec, name, task_spec, maximum, condition, test_before, **kwargs):
        super().__init__(wf_spec, name, **kwargs)
        self.task_spec = task_spec
        self.maximum = maximum
        self.condition = condition
        self.test_before = test_before

    def _update_hook(self, my_task):

        super()._update_hook(my_task)
        child_running = self.process_children(my_task)
        if child_running:
            # We're in the middle of an iteration; we're not done and we can't create a new task
            return False
        elif self.loop_complete(my_task):
            # No children running and one of the completion conditions has been met; done
            return True
        else:
            # Execute again
            if my_task.state != TaskState.WAITING:
                my_task._set_state(TaskState.WAITING)
            child = my_task._add_child(self.task_spec, TaskState.READY)
            child.data = deepcopy(my_task.data)

    def child_completed_action(self, my_task, child):
        DeepMerge.merge(my_task.data, child.data)

    def loop_complete(self, my_task):
        merged = my_task.internal_data.get('merged') or []
        if not self.test_before and len(merged) == 0:
            # "test before" isn't really compatible our execution model in a transparent way
            # This guarantees that the task will run at least once if test_before is False
            return False
        else:
            max_complete = self.maximum is not None and len(merged) >= self.maximum
            cond_complete = self.condition is not None and my_task.workflow.script_engine.evaluate(my_task, self.condition)
            return max_complete or cond_complete


class MultiInstanceTask(LoopTask):

    def __init__(self, wf_spec, name, task_spec, cardinality=None, data_input=None, 
                 data_output=None, input_item=None, output_item=None, condition=None,
                 **kwargs):

        super().__init__(wf_spec, name, **kwargs)
        self.task_spec = task_spec
        self.cardinality = cardinality
        self.data_input = data_input
        self.data_output = data_output
        self.input_item = input_item
        self.output_item = output_item
        self.condition = condition

    def child_completed_action(self, my_task, child):
        """This merges child data into this task's data."""

        if self.data_output is not None and self.output_item is not None:
            if self.output_item.name not in child.data:
                self.raise_data_exception("Expected an output item", child)
            item = child.data[self.output_item.name]
            key_or_index = child.internal_data.get('key_or_index')
            data_output = my_task.data[self.data_output.name]
            data_input = my_task.data[self.data_input.name] if self.data_input is not None else None
            if isinstance(data_output, Mapping) or data_input is data_output:
                data_output[key_or_index] = item
            else:
                data_output.append(item)
        else:
            DeepMerge.merge(my_task.data, child.data)

    def create_child(self, my_task, item, key_or_index=None):

        child = my_task._add_child(self.task_spec, TaskState.READY)
        child.data = deepcopy(my_task.data)
        if self.input_item is not None:
            child.data[self.input_item.name] = deepcopy(item)
        if key_or_index is not None:
            child.internal_data['key_or_index'] = key_or_index

    def check_completion_condition(self, my_task):

        merged = my_task.internal_data.get('merged', [])
        if len(merged) > 0:
            last_child = [c for c in my_task.children if str(c.id) == merged[-1]][0]
            return my_task.workflow.script_engine.evaluate(last_child, self.condition)

    def init_data_output_with_input_data(self, my_task, input_data):

        name = self.data_output.name
        if name not in my_task.data:
            if isinstance(input_data, (MutableMapping, MutableSequence)):
                # We can use the same class if it implements __setitem__
                my_task.data[name] = input_data.__class__()
            elif isinstance(input_data, Mapping):
                # If we have a map without __setitem__, use a dict
                my_task.data[name] = dict()
            else:
                # For all other types, we'll append to a list
                my_task.data[name] = list()
        else:
            output_data = my_task.data[self.data_output.name]
            if not isinstance(output_data, (MutableSequence, MutableMapping)):
                self.raise_data_exception("Only a mutable map (dict) or sequence (list) can be used for output", my_task)
            if input_data is not output_data and not isinstance(output_data, Mapping) and len(output_data) > 0:
                self.raise_data_exception(
                    "If the input is not being updated in place, the output must be empty or it must be a map (dict)", my_task)

    def init_data_output_with_cardinality(self, my_task):

        name = self.data_output.name
        if name not in my_task.data:
            my_task.data[name] = list()
        elif not isinstance(my_task.data[name], MutableSequence) or len(my_task.data[name]) > 0:
            self.raise_data_exception("If loop cardinality is specificied, the output must be a map (dict) or empty sequence (list)")

    def raise_data_exception(self, message, my_task):
        raise WorkflowDataException(message, my_task, data_input=self.data_input, data_output=self.data_output)


class SequentialMultiInstanceTask(MultiInstanceTask):

    def _update_hook(self, my_task):

        if my_task.state != TaskState.WAITING:
            super()._update_hook(my_task)

        child_running = self.process_children(my_task)
        if child_running:
            return False
        if self.condition is not None and self.check_completion_condition(my_task):
            return True
        else:
            return self.add_next_child(my_task)

    def add_next_child(self, my_task):

        if self.data_input is not None:
            key_or_index, item = self.get_next_input_item(my_task)
        else:
            key_or_index, item = self.get_next_index(my_task)

        if item is not None:
            if my_task.state != TaskState.WAITING:
                my_task._set_state(TaskState.WAITING)
            self.create_child(my_task, item, key_or_index)
        else:
            return True

    def get_next_input_item(self, my_task):

        input_data = my_task.data[self.data_input.name]
        remaining = my_task.internal_data.get('remaining')

        if remaining is None:
            remaining = self.init_remaining_items(my_task)
            if self.data_output is not None:
                self.init_data_output_with_input_data(my_task, input_data)

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

    def init_remaining_items(self, my_task):

        if self.data_input.name not in my_task.data:
            self.raise_data_exception("Missing data input for multiinstance task", my_task)
        input_data = my_task.data[self.data_input.name]

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

    def get_next_index(self, my_task):

        current = my_task.internal_data.get('current')
        if current is None:
            current = 0
            if self.data_output is not None:
                self.init_data_output_with_cardinality(my_task)

        if current < self.cardinality:
            # If using loop cardinalty, if a data input was specified, use the index as the "item"
            my_task.internal_data['current'] = current + 1
            return None, current
        else:
            return None, None


class ParallelMultiInstanceTask(MultiInstanceTask):
    
    def _update_hook(self, my_task):

        if my_task.state != TaskState.WAITING:
            super()._update_hook(my_task)
            self.create_children(my_task)

        child_running = self.process_children(my_task)
        if self.condition is not None and self.check_completion_condition(my_task):
            for child in my_task.children:
                if child.task_spec == self.task_spec and child.state != TaskState.COMPLETED:
                    child.cancel()
            return True
        return not child_running

    def create_children(self, my_task):

        data_input = my_task.data[self.data_input.name] if self.data_input is not None else None
        if data_input is not None:
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
            children = ((None, idx) for idx in range(self.cardinality))

        if not my_task.internal_data.get('started', False):

            if self.data_input is not None:
                self.init_data_output_with_input_data(my_task, my_task.data[self.data_input.name])
            else:
                self.init_data_output_with_cardinality(my_task)

            my_task._set_state(TaskState.WAITING)
            for key_or_index, item in children:
                self.create_child(my_task, item, key_or_index)

            my_task.internal_data['started'] = True
        else:
            return len(my_task.internal_data.get('merged', [])) == len(children)


def getDynamicMIClass():
    pass