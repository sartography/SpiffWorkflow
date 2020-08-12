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
from SpiffWorkflow.exceptions import WorkflowTaskExecException

from .FeelLikeScriptEngine import FeelLikeScriptEngine
from ..operators import Operator


class BpmnFeelScriptEngine(FeelLikeScriptEngine):
    """
    Used during execution of a BPMN workflow to evaluate condition / value
    expressions. These are used by Gateways, and by Catching Events
    (non-message ones).

    Also used to execute scripts.

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a mini-language of your own.
    """

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
                return super().evaluate(expression, **task.data)
        except Exception as e:
            raise WorkflowTaskExecException(task,
                                            "Error evaluating expression "
                                            "'%s', %s" % (expression, str(e)))

