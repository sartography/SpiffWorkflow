# -*- coding: utf-8 -*-

# Copyright (C) 2007 Samuel Abels
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
from .base import TaskSpec
from .Trigger import Trigger


class Choose(Trigger):

    """
    This class implements a task that causes an associated MultiChoice
    task to select the tasks with the specified name.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, wf_spec, name, context, choice=None, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  context: str
        :param context: The name of the MultiChoice that is instructed to
                        select the specified outputs.
        :type  choice: list(str)
        :param choice: The list of task spec names that is selected.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        assert wf_spec is not None
        assert name is not None
        assert context is not None
        # HACK: inherit from TaskSpec (not Trigger) on purpose.
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.context = context
        self.choice = choice is not None and choice or []

    def _on_complete_hook(self, my_task):
        context = my_task.workflow.get_task_spec_from_name(self.context)
        triggered = []
        for task in my_task.workflow.task_tree:
            if task.thread_id != my_task.thread_id:
                continue
            if task.task_spec == context:
                task.trigger(self.choice)
                triggered.append(task)
        for task in triggered:
            context._predict(task)
        TaskSpec._on_complete_hook(self, my_task)

    def serialize(self, serializer):
        return serializer.serialize_choose(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_choose(wf_spec, s_state)
