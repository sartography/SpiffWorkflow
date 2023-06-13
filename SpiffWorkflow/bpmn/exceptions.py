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
import re

from SpiffWorkflow.util import levenshtein
from SpiffWorkflow.exceptions import WorkflowException


class WorkflowTaskException(WorkflowException):
    """WorkflowException that provides task_trace information."""

    def __init__(self, error_msg, task=None, exception=None, line_number=None, offset=None, error_line=None):
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

    @staticmethod
    def get_task_trace(task):
        task_trace = [f"{task.task_spec.bpmn_name} ({task.workflow.spec.file})"]
        top = task.workflow.top_workflow
        parent = None if task.workflow is top else task.workflow.parent_workflow
        while parent is not None:
            caller = parent.get_task_from_id(task.workflow.parent_task_id)
            task_trace.append(f"{caller.task_spec.bpmn_name} ({parent.spec.file})")
            parent = None if caller.workflow is top else caller.workflow.parent_workflow
        return task_trace

    @staticmethod
    def did_you_mean_from_name_error(name_exception, options):
        """Returns a string along the lines of 'did you mean 'dog'? Given
        a name_error, and a set of possible things that could have been called,
        or an empty string if no valid suggestions come up. """
        def_match = re.match("name '(.+)' is not defined", str(name_exception))
        if def_match:
            bad_variable = re.match("name '(.+)' is not defined", str(name_exception)).group(1)
            most_similar = levenshtein.most_similar(bad_variable, options, 3)
            error_msg = ""
            if len(most_similar) == 1:
                error_msg += f' Did you mean \'{most_similar[0]}\'?'
            if len(most_similar) > 1:
                error_msg += f' Did you mean one of \'{most_similar}\'?'
            return error_msg


class WorkflowDataException(WorkflowTaskException):

    def __init__(self, message, task, data_input=None, data_output=None):
        """
        :param task: the task that generated the error
        :param data_input: the spec of the input variable (if a data input)
        :param data_output: the spec of the output variable (if a data output)
        """
        super().__init__(message, task)
        self.data_input = data_input
        self.data_output = data_output
