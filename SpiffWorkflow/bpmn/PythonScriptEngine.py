# -*- coding: utf-8 -*-
from builtins import object
import ast
import re
import datetime
import operator
from datetime import timedelta
from decimal import Decimal
from SpiffWorkflow.workflow import WorkflowException
from box import Box
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


default_header = """



"""
class PythonScriptEngine(object):
    """
    This should serve as a base for all scripting & expression evaluation
    operations that are done within both BPMN and BMN. Eventually it will also
    serve as a base for FEEL expressions as well

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a mini-language of your own.
    """
    def __init__(self):
        pass

    def validateExpression (self,text):
        if text is None:
            return
        try:
            # this should work if we can just do a straight equality
            ast.parse(text)
            return text,True
        except:
            try:
                revised_text = 's ' + text  # if we have problems parsing,
                # then we introduce a
                # variable on the left hand side and try that and see if that parses. If so, then we know that
                # we do not need to introduce an equality operator later in the dmn
                ast.parse(revised_text)
                return revised_text[2:],False
            except Exception as e:
                raise Exception("error parsing expression "+text + " " +
                                str(e))

    def eval_dmn_expression(self, inputExpr, matchExpr, **kwargs):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume it is equality.
        """
        if matchExpr is None:
            return True
        rhs, needsEquals = self.validateExpression(matchExpr)
        lhs, lhsNeedsEquals = self.validateExpression(inputExpr)
        if not lhsNeedsEquals:
            raise WorkflowException("Input Expression '%s' is malformed"%inputExpr)
        if needsEquals:
           expression = lhs + ' == ' + rhs
        else:
            expression = lhs + rhs
        return self.evaluate(default_header + expression, **kwargs)

    def evaluate(self, expression,externalMethods={}, **kwargs):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        exp,valid = self.validateExpression(expression)
        return self._eval(exp, **kwargs,externalMethods=externalMethods)

    def execute(self, task, script, data,externalMethods={}):
        """
        Execute the script, within the context of the specified task
        """


        globals = {'timedelta':timedelta,
                   'datetime':datetime}

        for x in data.keys():
            if isinstance(data[x],dict):
                data[x] = Box(data[x])
        #data.update({'task':task}) # one of our legacy tests is looking at task.
                                   # this may cause a problem down the road if we
                                   # actually have a variable named 'task'
        globals.update(data)   # dict comprehensions cause problems when the variables are not viable.
        globals.update(externalMethods)
        exec(script,globals,data)


    def _eval(self, expression,externalMethods={}, **kwargs):
        lcls = {}
        lcls.update(kwargs)
        globals = {'timedelta':timedelta,
                   'datetime':datetime}
        for x in lcls.keys():
            if isinstance(lcls[x], dict):
                lcls[x] = Box(lcls[x])
        globals.update(lcls)
        globals.update(externalMethods)
        return eval(expression,globals,lcls)
