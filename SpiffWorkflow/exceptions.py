# -*- coding: utf-8 -*-
from __future__ import division


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
import re

from .util import levenshtein


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
        Exception.__init__(self, '%s: %s' % (sender.name, error))
        # Points to the TaskSpec that generated the exception.
        self.sender = sender


class WorkflowTaskExecException(WorkflowException):
    """
    Exception during execution of task "payload". For example:

    * ScriptTask during execution of embedded script,
    * ServiceTask during external service call.
    """

    def __init__(self, task, error_msg, exception=None, line_number=0, error_line=""):
        """
        Exception initialization.

        :param task: the task that threw the exception
        :type task: Task
        :param exception: a human readable error message
        :type exception: Exception

        """

        self.offset = 0
        self.line_number = line_number
        self.task = task
        self.exception = exception
        self.error_line = error_line
        # If encountered in a sub-workflow, this traces back up the stack
        # so we can tell how we got to this paticular task, no matter how
        # deeply nested in sub-workflows it is.  Takes the form of:
        # task-description (file-name)
        self.task_trace = self.get_task_trace(task)

        if isinstance(exception, SyntaxError):
            # Prefer line number from syntax error if available.
            self.line_number = exception.lineno
            self.offset = exception.offset
        elif isinstance(exception, NameError):
            # Use Levenshitein to find most simiar items.
            bad_variable = re.match("name '(.+)' is not defined", str(exception)).group(1)
            most_similar = levenshtein.most_similar(bad_variable, task.data.keys(), 3)
            error_msg = f'something you are referencing does not exist: ' \
                            f'"{exception}".'
            error_msg += f' Did you mean \'{most_similar}\'?'

        WorkflowException.__init__(self, task.task_spec, error_msg)

    @staticmethod
    def get_task_trace(task):
        task_trace = []
        back_task = task
        last_workflow = None
        while True:
            if back_task.workflow != last_workflow:
                task_trace.append(f"{back_task.task_spec.description} "
                                  f"({back_task.workflow.spec.file})")
                last_workflow = back_task.workflow
            if back_task.parent and back_task != back_task.parent:
                back_task = back_task.parent
            else:
                break
        return task_trace


class StorageException(Exception):
    pass
