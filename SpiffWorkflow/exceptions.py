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
import re

from SpiffWorkflow.util import levenshtein


class SpiffWorkflowException(Exception):
    """
    Base class for all SpiffWorkflow-generated exceptions.
    """
    def __init__(self, msg):
        super().__init__(msg)
        self.notes = []

    def add_note(self, note):
        """add_note is a python 3.11 feature, this can be removed when we
        stop supporting versions prior to 3.11"""
        self.notes.append(note)

    def __str__(self):
        return super().__str__() + ". " + ". ".join(self.notes)


class WorkflowException(SpiffWorkflowException):
    """
    Base class for all SpiffWorkflow-generated exceptions.
    """

    def __init__(self, message, task_spec=None):
        """
        Standard exception class.

        :param task_spec: the task spec that threw the exception
        :type task_spec: TaskSpec
        :param error: a human-readable error message
        :type error: string
        """
        super().__init__(str(message))
        # Points to the TaskSpec that generated the exception.
        self.task_spec = task_spec

    @staticmethod
    def get_task_trace(task):
        task_trace = [f"{task.task_spec.description} ({task.workflow.spec.file})"]
        workflow = task.workflow
        while workflow != workflow.outer_workflow:
            caller = workflow.name
            workflow = workflow.outer_workflow
            task_trace.append(f"{workflow.spec.task_specs[caller].description} ({workflow.spec.file})")
        return task_trace

    @staticmethod
    def did_you_mean_from_name_error(name_exception, options):
        """Returns a string along the lines of 'did you mean 'dog'? Given
        a name_error, and a set of possible things that could have been called,
        or an empty string if no valid suggestions come up. """
        if isinstance(name_exception, NameError):
            def_match = re.match("name '(.+)' is not defined", str(name_exception))
            if def_match:
                bad_variable = re.match("name '(.+)' is not defined",
                                        str(name_exception)).group(1)
                most_similar = levenshtein.most_similar(bad_variable,
                                                        options, 3)
                error_msg = ""
                if len(most_similar) == 1:
                    error_msg += f' Did you mean \'{most_similar[0]}\'?'
                if len(most_similar) > 1:
                    error_msg += f' Did you mean one of \'{most_similar}\'?'
                return error_msg


class WorkflowTaskException(WorkflowException):
    """WorkflowException that provides task_trace information."""

    def __init__(self, error_msg, task=None, exception=None,
                 line_number=None, offset=None, error_line=None):
        """
        Exception initialization.

        :param task: the task that threw the exception
        :type task: Task
        :param error_msg: a human readable error message
        :type error_msg: str
        :param exception: an exception to wrap, if any
        :type exception: Exception
        """

        self.task = task
        self.line_number = line_number
        self.offset = offset
        self.error_line = error_line
        if exception:
            self.error_type = exception.__class__.__name__
        else:
            self.error_type = "unknown"
        super().__init__(error_msg, task_spec=task.task_spec)

        if isinstance(exception, SyntaxError) and not line_number:
            # Line number and offset can be recovered directly from syntax errors,
            # otherwise they must be passed in.
            self.line_number = exception.lineno
            self.offset = exception.offset
        elif isinstance(exception, NameError):
            self.add_note(self.did_you_mean_from_name_error(exception, list(task.data.keys())))

        # If encountered in a sub-workflow, this traces back up the stack,
        # so we can tell how we got to this particular task, no matter how
        # deeply nested in sub-workflows it is.  Takes the form of:
        # task-description (file-name)
        self.task_trace = self.get_task_trace(task)



class StorageException(SpiffWorkflowException):
    pass


class TaskNotFoundException(WorkflowException):
    pass
