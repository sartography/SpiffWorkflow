# -*- coding: utf-8 -*-
import copy
import re
import sys
import traceback
from builtins import object
import ast
import datetime
from datetime import timedelta
from decimal import Decimal

import dateparser
import pytz

from ..exceptions import WorkflowTaskExecException
from ..operators import Operator
from ..workflow import WorkflowException


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

    def __init__(self, scriptingAdditions=None):
        if scriptingAdditions is None:
            scriptingAdditions = {}
        self.globals = {'timedelta': timedelta,
                        'datetime': datetime,
                        'dateparser': dateparser,
                        'pytz': pytz,
                        'Box': Box,
                        }
        self.globals.update(scriptingAdditions)

    def validate_expression(self, text):
        if text is None:
            return
        try:
            # this should work if we can just do a straight equality
            ast.parse(text)
            return text, True
        except:
            try:
                revised_text = 's ' + text  # if we have problems parsing,
                # then we introduce a variable on the left hand side and try
                # that and see if that parses. If so, then we know that we do
                # not need to introduce an equality operator later in the dmn
                ast.parse(revised_text)
                return revised_text[2:], False
            except Exception as e:
                raise Exception("error parsing expression " + str(text) + " " +
                                str(e))

    def eval_dmn_expression(self, inputExpr, matchExpr, context, task=None):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume
         it is equality.

         An optional task can be included if this is being executed in the
         context of a BPMN task.
        """
        if matchExpr is None:
            return True

        nolhs = False
        # NB - the question mark allows us to do a double ended test - for
        # example - our input expr is 5 and the match expr is 4 < ? < 6  -
        # this should evaluate as 4  < 5 < 6 and it should evaluate as 'True'
        # NOTE:  It should only do this replacement outside of quotes.
        # for example, provided "This thing?"  in quotes, it should not
        # do the replacement.
        matchExpr = re.sub('(\?)(?=(?:[^\'"]|[\'"][^\'"]*[\'"])*$)',
                           'dmninputexpr', matchExpr)
        if 'dmninputexpr' in matchExpr:
            nolhs = True

        rhs, needsEquals = self.validate_expression(matchExpr)

        external_methods = {
            'datetime': datetime,
            'timedelta': timedelta,
            'Decimal': Decimal,
            'Box': Box
        }

        lhs, lhsNeedsEquals = self.validate_expression(inputExpr)
        if not lhsNeedsEquals:
            raise WorkflowException(
                "Input Expression '%s' is malformed" % inputExpr)
        if nolhs:
            dmninputexpr = self._evaluate(lhs, context, task, external_methods)
            external_methods['dmninputexpr'] = dmninputexpr
            return self._evaluate(rhs, context, task, external_methods)
        if needsEquals:
            expression = lhs + ' == ' + rhs
        else:
            expression = lhs + rhs

        return self._evaluate(expression, context, task, external_methods)

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
                return self._evaluate(expression, task.data, task=task)
        except Exception as e:
            raise WorkflowTaskExecException(task,
                                            "Error evaluating expression "
                                            "'%s', %s" % (expression, str(e)))

    def _evaluate(self, expression, context, task=None, external_methods=None):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        if external_methods is None:
            external_methods = {}

        expression, valid = self.validate_expression(expression)
        lcls = {}
        if isinstance(context, dict):
            lcls.update(context)

        globals = copy.copy(self.globals)  # else we pollute all later evals.
        for x in lcls.keys():
            if isinstance(lcls[x], Box):
                pass # Stunning performance improvement with this line.
            elif isinstance(lcls[x], dict):
                lcls[x] = Box(lcls[x])
        globals.update(lcls)
        globals.update(external_methods)
        return eval(expression, globals, lcls)

    def convertToBoxSub(self, data):
        if isinstance(data, list):
            for x in range(len(data)):
                data[x] = self.convertToBoxSub(data[x])
            return data
        if isinstance(data, dict):
            for x in data.keys():
                if isinstance(data[x], dict):
                    data[x] = self.convertToBoxSub(data[x])
            return Box(data)
        return data

    def convertToBox(self, data):
        for key in data.keys():
            data[key] = self.convertToBoxSub(data[key])

    def execute(self, task, script, data, external_methods=None):
        """
        Execute the script, within the context of the specified task
        """
        if external_methods is None:
            external_methods = {}
        globals = copy.copy(self.globals)

        self.convertToBox(data)
        globals.update(data)
        globals.update(external_methods)
        try:
            exec(script, globals, data)
        except WorkflowTaskExecException as wte:
            raise wte  # Something lower down is already raising a detailed error
        except Exception as err:
            detail = err.__class__.__name__
            if len(err.args) > 0:
                detail += ":" + err.args[0]
            line_number = 0
            error_line = ''
            cl, exc, tb = sys.exc_info()
            # Loop back through the stack trace to find the file called
            # 'string' - which is the script we are executing, then use that
            # to parse and pull out the offending line.
            for frameSummary in traceback.extract_tb(tb):
                if frameSummary.filename == '<string>':
                    line_number = frameSummary.lineno
                    error_line = script.splitlines()[line_number - 1]
            raise WorkflowTaskExecException(task, detail, err, line_number,
                                            error_line)

