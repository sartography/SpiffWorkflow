# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
from builtins import object
# Copyright (C) 2012 Matthew Hampton
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

from ..operators import Operator


class BpmnScriptEngine(object):

    """
    Used during execution of a BPMN workflow to evaluate condition / value expressions. These are used by
    Gateways, and by Catching Events (non-message ones).

    Also used to execute scripts.

    If you are uncomfortable with the use of eval() and exec, then you should provide a specialised
    subclass that parses and executes the scripts / expressions in a mini-language of your own.
    """

    def evaluate(self, task, expression):
        """
        Evaluate the given expression, within the context of the given task and return the result.
        """
        if isinstance(expression, Operator):
            return expression._matches(task)
        else:
            return self._eval(task, expression, **task.data)

    def execute(self, task, script, **kwargs):
        """
        Execute the script, within the context of the specified task
        """
        locals().update(kwargs)
        exec(script)

    def _eval(self, task, expression, **kwargs):
        locals().update(kwargs)
        return eval(expression)
