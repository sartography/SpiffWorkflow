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

import copy


class BasePythonScriptEngineEnvironment:
    def __init__(self, environment_globals=None):
        self.globals = environment_globals or {}

    def evaluate(self, expression, context, external_methods=None):
        raise NotImplementedError("Subclass must implement this method")

    def execute(self, script, context, external_methods=None):
        raise NotImplementedError("Subclass must implement this method")


class TaskDataEnvironment(BasePythonScriptEngineEnvironment):

    def evaluate(self, expression, context, external_methods=None):
        my_globals = copy.copy(self.globals)  # else we pollute all later evals.
        self._prepare_context(context)
        my_globals.update(external_methods or {})
        my_globals.update(context)
        return eval(expression, my_globals)

    def execute(self, script, context, external_methods=None):
        self.check_for_overwrite(context, external_methods or {})
        my_globals = copy.copy(self.globals)
        self._prepare_context(context)
        my_globals.update(external_methods or {})
        context.update(my_globals)
        try:
            exec(script, context)
        finally:
            self._remove_globals_and_functions_from_context(context, external_methods)
        return True

    def _prepare_context(self, context):
        pass

    def _remove_globals_and_functions_from_context(self, context, external_methods=None):
        """When executing a script, don't leave the globals, functions
        and external methods in the context that we have modified."""
        for k in list(context):
            if k == "__builtins__" or \
                    hasattr(context[k], '__call__') or \
                    k in self.globals or \
                    external_methods and k in external_methods:
                context.pop(k)

    def check_for_overwrite(self, context, external_methods):
        """It's possible that someone will define a variable with the
        same name as a pre-defined script, rendering the script un-callable.
        This results in a nearly indecipherable error.  Better to fail
        fast with a sensible error message."""
        func_overwrites = set(self.globals).intersection(context)
        func_overwrites.update(set(external_methods).intersection(context))
        if len(func_overwrites) > 0:
            msg = f"You have task data that overwrites a predefined " \
                  f"function(s). Please change the following variable or " \
                  f"field name(s) to something else: {func_overwrites}"
            raise ValueError(msg)
