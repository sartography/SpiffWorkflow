# Copyright (C) 2007 Samuel Abels, 2023 Sartography
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

from ..task import TaskState
from ..exceptions import WorkflowException
from .base import TaskSpec


class MultiChoice(TaskSpec):

    """
    This class represents an if condition where multiple conditions may match
    at the same time, creating multiple outgoing branches.
    This task has one or more inputs, and one or more incoming branches.
    This task has one or more outputs.
    """

    def __init__(self, wf_spec, name, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        super(MultiChoice, self).__init__(wf_spec, name, **kwargs)
        self.cond_task_specs = []
        self.choice = None

    def connect(self, taskspec):
        """
        Convenience wrapper around connect_if() where condition is set to None.
        """
        return self.connect_if(None, taskspec)

    def connect_if(self, condition, task_spec):
        """
        Connects a taskspec that is executed if the condition DOES match.

        condition -- a condition (Condition)
        taskspec -- the conditional task spec
        """
        assert task_spec is not None
        self._outputs.append(task_spec.name)
        self.cond_task_specs.append((condition, task_spec.name))
        task_spec._connect_notify(self)

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        TaskSpec.test(self)
        if len(self.cond_task_specs) < 1:
            raise WorkflowException('At least one output required.', task_spec=self)
        for condition, name in self.cond_task_specs:
            if name is None:
                raise WorkflowException('Condition with no task spec.', task_spec=self)
            task_spec = self._wf_spec.get_task_spec_from_name(name)
            if task_spec is None:
                msg = 'Condition leads to non-existent task ' + repr(name)
                raise WorkflowException(msg, task_spec=self)
            if condition is None:
                continue

    def _on_trigger(self, my_task, choice):
        """
        Lets a caller narrow down the choice by using a Choose trigger.
        """
        self.choice = choice
        # The caller needs to make sure that predict() is called.

    def _predict_hook(self, my_task):
        conditional, unconditional = [], []
        for condition, output in self.cond_task_specs:
            if self.choice is not None and output not in self.choice:
                continue
            if condition is None:
                unconditional.append(my_task.workflow.spec.get_task_spec_from_name(output))
            else:
                conditional.append(my_task.workflow.spec.get_task_spec_from_name(output))
        state = TaskState.MAYBE if my_task.state == TaskState.MAYBE else TaskState.LIKELY
        my_task._sync_children(unconditional, state)
        for spec in conditional:
            my_task._add_child(spec, TaskState.MAYBE)

    def _get_matching_outputs(self, my_task):
        outputs = []
        for condition, output in self.cond_task_specs:
            if self.choice is not None and output not in self.choice:
                continue
            if condition is None or condition._matches(my_task):
                outputs.append(my_task.workflow.spec.get_task_spec_from_name(output))
        return outputs

    def _run_hook(self, my_task):
        """Runs the task. Should not be called directly."""
        my_task._sync_children(self._get_matching_outputs(my_task), TaskState.FUTURE)
        for child in my_task.children:
            child.task_spec._predict(child, mask=TaskState.FUTURE|TaskState.PREDICTED_MASK)
        return True

    def serialize(self, serializer):
        return serializer.serialize_multi_choice(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_multi_choice(wf_spec, s_state)
