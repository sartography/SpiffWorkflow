# -*- coding: utf-8 -*-
from builtins import object
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


class PythonSriptEngine(object):
    """
    This should serve as a base for all scripting & expression evaluation
    operations that are done within both BPMN and BMN. Eventually it will also
    serve as a base for FEEL expressions as well

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a mini-language of your own.
    """
    def eval_bmn_expression(self,task,inputExpr,matchExpr):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume it is equality.
        """
        expression = inputExpr + ' == ' + matchExpr
        self.evaluate(task,expression)

    def evaluate(self, task, expression):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
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
