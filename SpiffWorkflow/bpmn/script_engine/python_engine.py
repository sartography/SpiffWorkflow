# Copyright (C) 2020 Kelly McDonald, 2023 Sartography
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

import ast
import sys
import traceback

from SpiffWorkflow.exceptions import SpiffWorkflowException
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException
from .python_environment import TaskDataEnvironment


class PythonScriptEngine(object):
    """
    This should serve as a base for all scripting & expression evaluation
    operations that are done within both BPMN and BMN. Eventually it will also
    serve as a base for FEEL expressions as well

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a different way.
    """

    def __init__(self, environment=None):
        self.environment = environment or TaskDataEnvironment()

    def validate(self, expression):
        ast.parse(expression)

    def evaluate(self, task, expression, external_context=None):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        try:
            return self._evaluate(expression, task.data, external_context)
        except SpiffWorkflowException as se:
            se.add_note(f"Error evaluating expression '{expression}'")
            raise se
        except Exception as e:
            raise WorkflowTaskException(f"Error evaluating expression '{expression}'", task=task, exception=e)

    def execute(self, task, script, external_context=None):
        """Execute the script, within the context of the specified task."""
        try:
            return self._execute(script, task.data, external_context or {})
        except Exception as err:
            wte = self.create_task_exec_exception(task, script, err)
            raise wte

    def call_service(self, operation_name, operation_params, task_data):
        """Override to control how external services are called from service
        tasks."""
        raise NotImplementedError("To call external services override the script engine and implement `call_service`.")

    def create_task_exec_exception(self, task, script, err):
        line_number, error_line = self.get_error_line_number_and_content(script, err)
        if isinstance(err, SpiffWorkflowException):
            err.line_number = line_number
            err.error_line = error_line
            err.add_note(f"Python script error on line {line_number}: '{error_line}'")
            return err
        detail = err.__class__.__name__
        if len(err.args) > 0:
            detail += ":" + err.args[0]
        return WorkflowTaskException(detail, task=task, exception=err, line_number=line_number, error_line=error_line)

    def get_error_line_number_and_content(self, script, err):
        line_number = 0
        error_line = ''
        if isinstance(err, SyntaxError):
            line_number = err.lineno
        else:
            cl, exc, tb = sys.exc_info()
            # Loop back through the stack trace to find the file called
            # 'string' - which is the script we are executing, then use that
            # to parse and pull out the offending line.
            for frame_summary in traceback.extract_tb(tb):
                if frame_summary.filename == '<string>':
                    line_number = frame_summary.lineno
        if line_number > 0:
            error_line = script.splitlines()[line_number - 1]
        return line_number, error_line

    def _evaluate(self, expression, context, external_context=None):
        return self.environment.evaluate(expression, context, external_context)

    def _execute(self, script, context, external_context=None):
        return self.environment.execute(script, context, external_context)
