# -*- coding: utf-8 -*-

# Copyright (C) 2021 Sartography
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
from ..task import TaskState
from SpiffWorkflow.exceptions import WorkflowTaskException


class LoopResetTask(TaskSpec):

    """
    This task is used as a placeholder when we are going to loopback
    to a previous point in the workflow.  When this task is completed,
    it will reset the workflow back to a previous point.
    """

    def __init__(self, wf_spec, name, destination_id, destination_spec_name, **kwargs):
        """
        Constructor.

        :param script: the script that must be executed by the script engine.
        """
        super(LoopResetTask, self).__init__(wf_spec, name, **kwargs)
        self.destination_id = destination_id
        self.destination_spec_name = destination_spec_name

    def _on_complete_hook(self, task):
        try:
            # Prefer the exact task id, but if not available, use the
            # last instance of the task_spec.
            destination = task.workflow.get_task(self.destination_id)
            if not destination:
                destination = task.workflow.get_tasks_from_spec_name(
                    self.destination_spec_name)[-1]

            destination.reset_token(task.data, reset_data=False)
        except Exception as e:
            # set state to WAITING (because it is definitely not COMPLETED)
            # and raise WorkflowException pointing to this task because
            # maybe upstream someone will be able to handle this situation
            task._set_state(TaskState.WAITING)
            if isinstance(e, WorkflowTaskException):
                raise e
            else:
                raise WorkflowTaskException(
                    task, 'Error during loop back:' + str(e), e)
        super(LoopResetTask, self)._on_complete_hook(task)

    def serialize(self, serializer):
        return serializer.serialize_loop_reset_task(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer.deserialize_loop_reset_task(wf_spec, s_state)

