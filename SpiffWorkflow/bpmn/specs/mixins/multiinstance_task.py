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

from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.util.deep_merge import DeepMerge
from SpiffWorkflow.bpmn.specs.bpmn_task_spec import BpmnTaskSpec
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException


class LoopTask(BpmnTaskSpec):

    def _merged_children(self, my_task):
        return my_task.internal_data.get('merged', [])
    
    def _instances(self, my_task):
        return filter(lambda c: c.task_spec.name == self.task_spec, my_task.children)

    def is_instance(self, my_task, child):
        return child.parent is my_task and child.task_spec.name == self.task_spec

    def _instances_after(self, my_task, child):
        """Instances that only exist because `child` finished (none when instances run in parallel)."""
        instances = list(self._instances(my_task))
        return instances[instances.index(child) + 1:]

    def reset_instance(self, my_task, child):
        """Return the loop to the point where `child` was its unfinished instance.

        A workflow calls this before it resets `child` (or a task inside it).  The
        loop forgets that `child` and anything that followed it were merged, and
        its own data is put back the way it was while `child` was running.

        Returns the children of `my_task` that are no longer valid: later instances
        and whatever followed the loop.  The caller removes them from the tree.
        """
        instances = list(self._instances(my_task))
        later = self._instances_after(my_task, child)
        discard = {str(task.id) for task in [child] + later}
        merged = self._merged_children(my_task)
        # Remember where each instance stood, so that one merged again goes back to its place
        order = my_task.internal_data.get('merge_order', [])
        my_task.internal_data['merge_order'] = order + [m for m in merged if m not in order]
        my_task.internal_data['merged'] = [m for m in merged if m not in discard]
        self._rewind(my_task, child)
        return later + [task for task in my_task.children if task not in instances]

    def _rewind(self, my_task, child):
        # The loop's data is the data it started with plus the results of the
        # instances that still count.  Completing the loop may have changed it
        # since (a post script, data outputs), so build it again.
        self._restore_data_at_start(my_task, child)
        instances = {str(instance.id): instance for instance in self._instances(my_task)}
        for merged in self._merged_children(my_task):
            self.merge_data(my_task, instances[merged])

    def _restore_data_at_start(self, my_task, child):
        """Give the loop back the data it started with; returns False if no copy of it was kept.

        An instance that is a subprocess copies the loop's data into its start
        task, and a reset inside the subprocess never touches that task.  (A call
        activity with declared data inputs copies only those, so it keeps no copy.)"""
        first = next(self._instances(my_task), None)
        subprocess = first and my_task.workflow.top_workflow.subprocesses.get(first.id)
        if subprocess is None or getattr(subprocess.spec.io_specification, 'data_inputs', None):
            return False
        my_task.data = deepcopy(subprocess.task_tree.data)
        return True

    def _merge(self, my_task, child):
        """Merge `child` where it stood before a reset took it out; otherwise after the others."""
        merged, child_id = my_task.internal_data['merged'], str(child.id)
        order = my_task.internal_data.get('merge_order', [])
        position = len(merged)
        if child_id in order:
            position = sum(1 for m in merged if m in order and order.index(m) < order.index(child_id))
        self.merge_data(my_task, child, position)
        merged.insert(position, child_id)

    def merge_data(self, my_task, child, position=None):
        # Merging changes nested values in place, and tasks can share those with
        # each other.  Merge copies, so no other task's data changes with the loop's.
        data = deepcopy(my_task.data)
        DeepMerge.merge(data, deepcopy(child.data))
        my_task.data = data

    def instance_data(self, my_task, child):
        """The data `child` starts with."""
        return deepcopy(my_task.data)

    def restore_instance(self, child, internal_data):
        """Give a reset instance back its place in the loop; a reset clears a task's internal data."""
        child.triggered = True
        for key in ('iteration', 'key_or_index', 'item'):
            if key in internal_data:
                child.internal_data[key] = internal_data[key]


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
        info['instance_map'] = {idx: str(t.id) for idx, t in enumerate(self._instances(my_task))}
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
        self._merge(my_task, child)
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
        self._merge(my_task, child)

    def merge_data(self, my_task, child, position=None):
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
                data_output.insert(len(data_output) if position is None else position, item)
        else:
            super().merge_data(my_task, child)

    def _restore_data_at_start(self, my_task, child):
        if super()._restore_data_at_start(my_task, child):
            if self.input_item is not None:
                my_task.data.pop(self.input_item.bpmn_id, None)  # the first instance's own item
            return True
        # No copy was kept, so undo what completing the loop did to its data.  It
        # removed the inputs copied from data objects (see BpmnTaskSpec._on_complete_hook);
        # the instance still holds them, and the data objects may have changed since.
        for obj in self.data_input_associations:
            if obj.bpmn_id not in my_task.data and obj.bpmn_id in child.data:
                my_task.data[obj.bpmn_id] = deepcopy(child.data[obj.bpmn_id])
        # And it had collected every instance's output.  Empty the output, unless the
        # input is updated in place: there each instance only overwrites its own entry.
        if self.data_output is not None and self.output_item is not None:
            data_input = self.data_input.get(my_task) if self.data_input is not None else None
            if not self.data_output.exists(my_task) or self.data_output.get(my_task) is not data_input:
                my_task.data.pop(self.data_output.bpmn_id, None)
                if self.data_input is not None:
                    self.init_data_output_with_input_data(my_task, data_input)
                else:
                    self.init_data_output_with_cardinality(my_task)
        return False

    def instance_data(self, my_task, child):
        data = super().instance_data(my_task, child)
        if self.input_item is not None and self.input_item.exists(child):
            data[self.input_item.bpmn_id] = deepcopy(self.input_item.get(child))
        return data

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
                self.data_output.set(my_task, {})
            else:
                # For all other types, we'll append to a list
                self.data_output.set(my_task, [])
        else:
            output_data = self.data_output.get(my_task)
            if not isinstance(output_data, (MutableSequence, MutableMapping)):
                self.raise_data_exception("Only a mutable map (dict) or sequence (list) can be used for output", my_task)
            if input_data is not output_data and not isinstance(output_data, Mapping) and len(output_data) > 0:
                self.raise_data_exception(
                    "If the input is not being updated in place, the output must be empty or it must be a map (dict)", my_task)

    def init_data_output_with_cardinality(self, my_task):

        if not self.data_output.exists(my_task):
            self.data_output.set(my_task, [])
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
        if not self.children_complete(my_task):
            self.add_next_child(my_task)
            my_task._set_state(TaskState.STARTED)
        else:
            return True

    def _rewind(self, my_task, child):
        super()._rewind(my_task, child)
        done = len(list(self._instances(my_task))) - len(self._instances_after(my_task, child))
        if self.data_input is not None:
            my_task.internal_data['remaining'] = self.init_remaining_items(my_task)[done:]
        else:
            my_task.internal_data['current'] = done

    def task_info(self, my_task):
        info = super().task_info(my_task)
        cardinality = my_task.internal_data.get('cardinality')
        if cardinality is not None:
            info['future'] = list(range(len(info['completed']) + len(info['running']), cardinality))
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
            remaining = list(range(len(input_data)))
        elif isinstance(input_data, Mapping):
            # For dicts, use the keys
            remaining = list(input_data)
        elif isinstance(input_data, Iterable):
            # Otherwise, just copy the objects as a last resort
            remaining = list(input_data)
        else:
            self.raise_data_exception("Multiinstance data input must be iterable", my_task)
        return remaining

    def children_complete(self, my_task):
        if self.data_input is not None:
            return len(my_task.internal_data.get('remaining', [])) == 0
        else:
            return my_task.internal_data.get('current', 0) == my_task.internal_data.get('cardinality', 0)


class ParallelMultiInstanceTask(MultiInstanceTask):

    def _instances_after(self, my_task, child):
        return []

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
