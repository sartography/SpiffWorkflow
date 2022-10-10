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


class WorkflowException(Exception):
    """
    Base class for all SpiffWorkflow-generated exceptions.
    """

    def __init__(self, sender, error):
        """
        Standard exception class.

        :param sender: the task spec that threw the exception
        :type sender: TaskSpec
        :param error: a human readable error message
        :type error: string
        """
        Exception.__init__(self, str(error))
        # Points to the TaskSpec that generated the exception.
        self.sender = sender

    @staticmethod
    def get_task_trace(task):
        task_trace = [f"{task.task_spec.description} ({task.workflow.spec.file})"]
        workflow = task.workflow
        while workflow != workflow.outer_workflow:
            caller = workflow.name
            workflow = workflow.outer_workflow
            task_trace.append(f"{workflow.spec.task_specs[caller].description} ({workflow.spec.file})")
        return task_trace

class WorkflowTaskException(WorkflowException):
    """WorkflowException that provides task_trace information."""

    def __init__(self, task, error_msg, exception=None):
        """
        Exception initialization.

        :param task: the task that threw the exception
        :type task: Task
        :param error_msg: a human readable error message
        :type error_msg: str
        :param exception: an exception to wrap, if any
        :type exception: Exception
        """

        self.exception = exception
        self.task = task

        # If encountered in a sub-workflow, this traces back up the stack
        # so we can tell how we got to this paticular task, no matter how
        # deeply nested in sub-workflows it is.  Takes the form of:
        # task-description (file-name)
        self.task_trace = self.get_task_trace(task)

        super().__init__(task.task_spec, error_msg)


class StorageException(Exception):
    pass
