# -*- coding: utf-8 -*-
import copy
import sys
import traceback
from builtins import object
import ast
import datetime
from datetime import timedelta

from SpiffWorkflow.exceptions import WorkflowTaskExecException
from SpiffWorkflow.workflow import WorkflowException

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
                    if isinstance(v,dict):
                        self[k] = Box(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = Box(v)
                else:
                    self[k] = v

    def __deepcopy__(self, memodict={}):
        my_copy = Box()
        for k,v in self.items():
            my_copy[k] = copy.deepcopy(v)
        return my_copy

    def __getattr__(self, attr):
        try:
            output = self[attr]
        except:
            raise AttributeError
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
    def __init__(self,scriptingAdditions = {}):
        self.globals = {'timedelta':timedelta,
                         'datetime':datetime,
                        'Box':Box,
                        }
        self.globals.update(scriptingAdditions)

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

        return self.evaluate(default_header + expression, do_convert=False, **kwargs)

    def evaluate(self, expression, external_methods=None, do_convert=True, **kwargs):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        if external_methods is None:
            external_methods = {}

        exp,valid = self.validateExpression(expression)
        return self._eval(exp, **kwargs,
                          do_convert=do_convert,
                          external_methods=external_methods)

    def convertToBoxSub(self,data):
        if isinstance(data,list):
            for x in range(len(data)):
                data[x] = self.convertToBoxSub(data[x])
            return data
        if isinstance(data,dict):
            for x in data.keys():
                if isinstance(data[x],dict):
                    data[x] = self.convertToBoxSub(data[x])
            return Box(data)
        return data


    def convertToBox(self,data):
        for key in data.keys():
            data[key] = self.convertToBoxSub(data[key])

    def convertFromBoxSub(self,data):
        if isinstance(data,list):
            return [self.convertFromBoxSub(x) for x in data]
        if isinstance(data,(dict,Box)):
            return {k:self.convertFromBoxSub(v) for k,v in data.items()}
        return data

    def convertFromBox(self,data):
        for k in data.keys():
            data[k] = self.convertFromBoxSub(data[k])

    def execute(self, task, script, data, external_methods=None):
        """
        Execute the script, within the context of the specified task
        """
        if external_methods is None:
            external_methods = {}
        globals = self.globals

        self.convertToBox(data)
        #data.update({'task':task}) # one of our legacy tests is looking at task.
                                   # this may cause a problem down the road if we
                                   # actually have a variable named 'task'
        globals.update(data)   # dict comprehensions cause problems when the variables are not viable.
        globals.update(external_methods)
        try:
            exec(script,globals,data)
        except SyntaxError as err:
            detail = err.args[0]
            line_number = err.lineno
            raise WorkflowTaskExecException(task, detail, err, line_number)
        except Exception as err:
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
            raise WorkflowTaskExecException(task, detail, err, line_number)


        self.convertFromBox(data)


    def _eval(self, expression,externalMethods={}, **kwargs):
        lcls = {}
        lcls.update(kwargs)
        globals = self.globals
        for x in lcls.keys():
            if isinstance(lcls[x], dict):
                lcls[x] = Box(lcls[x])
        globals.update(lcls)
        globals.update(externalMethods)
        return eval(expression,globals,lcls)
