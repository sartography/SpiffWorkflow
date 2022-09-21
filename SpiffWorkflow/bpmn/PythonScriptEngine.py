# -*- coding: utf-8 -*-
import ast
import copy
import sys
import traceback
import datetime

import dateparser
import pytz

from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from ..operators import Operator


# Copyright (C) 2020 Kelly McDonald
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


class Box(dict):
    """
    Example:
    m = Box({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Box, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = Box(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = Box(v)
                else:
                    self[k] = v

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        my_copy = Box()
        for k, v in self.items():
            my_copy[k] = copy.deepcopy(v)
        return my_copy

    def __getattr__(self, attr):
        try:
            output = self[attr]
        except:
            raise AttributeError(
                "Dictionary has no attribute '%s' " % str(attr))
        return output

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Box, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__init__(state)

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Box, self).__delitem__(key)
        del self.__dict__[key]


class PythonScriptEngine(object):
    """
    This should serve as a base for all scripting & expression evaluation
    operations that are done within both BPMN and BMN. Eventually it will also
    serve as a base for FEEL expressions as well

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a different way.
    """

    def __init__(self, scripting_additions=None):

        self.globals = {'timedelta': datetime.timedelta,
                        'datetime': datetime,
                        'dateparser': dateparser,
                        'pytz': pytz,
                        'Box': Box,
                        }
        self.globals.update(scripting_additions or {})
        self.running_tasks = {}
        self.error_tasks = {}

    def validate(self, expression):
        ast.parse(expression)

    def evaluate(self, task, expression):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        try:
            if isinstance(expression, Operator):
                # I am assuming that this takes care of some kind of XML
                # expression judging from the contents of operators.py
                return expression._matches(task)
            else:
                return self._evaluate(expression, task.data)
        except Exception as e:
            raise WorkflowTaskExecException(task, f"Error evaluating expression {expression}", e)

    def execute(self, task, script, external_methods=None):
        """
        Execute the script, within the context of the specified task
        """
        try:
            self.check_for_overwrite(task, external_methods or {})
            result = self._execute(script, task.data, external_methods or {})
            if result is not None:
                self.running_tasks[task.id] = result
        except Exception as err:
            wte = self.create_task_exec_exception(task, err)
            self.error_tasks[task.id] = wte
            raise wte

    def available_service_task_external_methods(self):
        """Allows consumers a hook to specify external methods that can be
        called from service tasks."""
        return None

    def evaluate_service_task_script(self, task, script, data,
            external_methods=None):
        """Evaluates the script, within the context of the specified task. Task
        is assumed to be a service task. service_task_external_methods are
        merged with the supplied external_methods before execution."""

        additions = self.available_service_task_external_methods()

        if external_methods is None:
            external_methods = {}

        external_methods.update(additions)

        return self._evaluate(script, task.data, external_methods=external_methods)

    def is_complete(self, task):

        if task.id in self.running_tasks:
            try:
                result = self._is_complete(self.running_tasks.get(task.id))
                if result is None:
                    del self.running_tasks[task.id]
                    return True
                else:
                    return False
            except Exception as err:
                self.error_tasks[task.id] = self.create_task_exec_exception(task, err)
                return False
        elif task.id in self.error_tasks:
            return False
        else:
            return True

    def create_task_exec_exception(self, task, err):

        if isinstance(err, WorkflowTaskExecException):
            return err

        detail = err.__class__.__name__
        if len(err.args) > 0:
            detail += ":" + err.args[0]
        line_number = 0
        error_line = ''
        cl, exc, tb = sys.exc_info()
        # Loop back through the stack trace to find the file called
        # 'string' - which is the script we are executing, then use that
        # to parse and pull out the offending line.
        for frame_summary in traceback.extract_tb(tb):
            if frame_summary.filename == '<string>':
                line_number = frame_summary.lineno
                error_line = task.task_spec.script.splitlines()[line_number - 1]
        return WorkflowTaskExecException(task, detail, err, line_number, error_line)

    def check_for_overwrite(self, task, external_methods):
        """It's possible that someone will define a variable with the
        same name as a pre-defined script, rending the script un-callable.
        This results in a nearly indecipherable error.  Better to fail
        fast with a sensible error message."""
        func_overwrites = set(self.globals).intersection(task.data)
        func_overwrites.update(set(external_methods).intersection(task.data))
        if len(func_overwrites) > 0:
            msg = f"You have task data that overwrites a predefined " \
                  f"function(s). Please change the following variable or " \
                  f"field name(s) to something else: {func_overwrites}"
            raise WorkflowTaskExecException(task, msg)

    def convert_to_box(self, data):
        if isinstance(data, dict):
            for x in data.keys():
                if isinstance(data[x], dict):
                    data[x] = self.convert_to_box(data[x])
            return Box(data)
        if isinstance(data, list):
            for x in range(len(data)):
                data[x] = self.convert_to_box(data[x])
            return data
        return data

    def _evaluate(self, expression, context, external_methods=None):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        lcls = {}
        if isinstance(context, dict):
            lcls.update(context)

        globals = copy.copy(self.globals)  # else we pollute all later evals.
        for key in lcls.keys():
            if isinstance(lcls[key], Box):
                pass # Stunning performance improvement with this line.
            elif isinstance(lcls[key], dict):
                lcls[key] = Box(lcls[key])
        globals.update(lcls)
        globals.update(external_methods or {})
        return eval(expression, globals, lcls)

    def _execute(self, script, context, external_methods=None):

        my_globals = copy.copy(self.globals)
        self.convert_to_box(context)
        my_globals.update(external_methods or {})
        context.update(my_globals)
        exec(script, context)
        self.remove_globals_and_functions_from_context(context, external_methods)

    def remove_globals_and_functions_from_context(self, context,
                                                  external_methods = None):
        """When executing a script, don't leave the globals, functions
        and external methods in the context that we return."""
        for k in list(context):
            if k == "__builtins__":
                context.pop(k)
            elif hasattr(context[k], '__call__'):
                context.pop(k)
            elif k in self.globals:
                context.pop(k)
            elif external_methods and k in external_methods:
                context.pop(k)

    def _is_complete(self, task):
        # The default is just to run exec in this process, so we'll never need this
        # However, an asynchronous execution environment can extend it with a polling
        # mechanism
        return True
