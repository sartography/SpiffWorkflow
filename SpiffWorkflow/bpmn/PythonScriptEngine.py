# -*- coding: utf-8 -*-
from builtins import object
import ast
import re
import datetime
from decimal import Decimal
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

def convertTime(datestr,parsestr):
    return datetime.datetime.strptime(datestr,parsestr)

class FeelInterval():
    def __init__(self, begin, end, leftOpen=False, rightOpen=False):
        # pesky thing with python floats and Decimal comparison
        if isinstance(begin,float):
            begin = Decimal("%0.5f"%begin)
        if isinstance(end, float):
            end = Decimal("%0.5f" % end)

        self.startInterval = begin
        self.endInterval = end
        self.leftOpen = leftOpen
        self.rightOpen = rightOpen

    def __eq__(self, other):
        if self.leftOpen:
            lhs = other > self.startInterval
        else:
            lhs = other >= self.startInterval
        if self.rightOpen:
            rhs = other < self.endInterval
        else:
            rhs = other <= self.endInterval
        return lhs and rhs

class FeelContains():
    def __init__(self, testItem,invert=False ):
        self.test = testItem
        self.invert = invert
    def __eq__(self, other):
        has = False
        if isinstance(other,dict):
            has = self.test in list(other.keys())
        else:
            has = self.test in list(other)
        if self.invert:
            return not has
        else:
            return has

class FeelNot():
    def __init__(self, testItem):
        self.test = testItem

    def __eq__(self, other):
        if other == self.test:
            return False
        else:
            return True

def expandDotDict(text):
    parts = text.split('.')
    suffix = ''.join(["['%s']"%x for x in parts[1:]])
    prefix = parts[0]
    return prefix+suffix

# Order Matters!!
fixes = [('not\s+?contains\((.+?)\)','FeelContains(\\1,invert=True)'), # not  contains('something')
         ('not\((.+?)\)','FeelNot(\\1)'),   # not('x')
         ('contains\((.+?)\)', 'FeelContains(\\1)'), # contains('x')
         ('date\s+?and\s+?time\s*\((.+?)\)','convertTime(\\1,"%Y-%m-%dT%H:%M:%S")'), # date  and time (<datestring>)
         ('\[([^\[\]]+?)[.]{2}([^\[\]]+?)\]','FeelInterval(\\1,\\2)'),                # closed interval on both sides
         ('[\]\(]([^\[\]\(\)]+?)[.]{2}([^\[\]\)\(]+?)\]','FeelInterval(\\1,\\2,leftOpen=True)'),  # open lhs
         ('\[([^\[\]\(\)]+?)[.]{2}([^\[\]\(\)]+?)[\[\)]','FeelInterval(\\1,\\2,rightOpen=True)'), # open rhs
         ('[\]\(]([^\[\]\(\)]+?)[.]{2}([^\[\]\(\)]+?)[\[\)]',
                'FeelInterval(\\1,\\2,rightOpen=True,leftOpen=True)'), # open both


         # parse dot.dict for several different edge cases
         # make sure that it begins with a letter character - otherwise we
         # may get float numbers.
         # will not work for cases where we do something like:
         #               x contains(this.dotdict.item)
         # and it may be difficult, because we do not want to replace for the case of
         #               somedict.keys()  - because that is actually in the tests.
         # however, it would be fixed by doing:
         #              x contains( this.dotdict.item )
         ('\s[a-zA-Z][a-zA-Z0-9.]+?\s',expandDotDict),  # In the middle of a string
         ('^[a-zA-Z][a-zA-Z0-9.]+?\s',expandDotDict),   # at beginning with stuff after
         ('^[a-zA-Z][a-zA-Z0-9.]+?$',expandDotDict),    # all by itself & lonely :-(
         ('\s[a-zA-Z][a-zA-Z0-9.]+?$',expandDotDict),   # at the very end of a string
         ('true','True'),
         ('false','False')
         ]


default_header = """



"""
class PythonSriptEngine(object):
    """
    This should serve as a base for all scripting & expression evaluation
    operations that are done within both BPMN and BMN. Eventually it will also
    serve as a base for FEEL expressions as well

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a mini-language of your own.
    """

    def patch_expression(self,invalid_python,lhs=''):
        if invalid_python is None:
            return None
        proposed_python = invalid_python
        for transformation in fixes:
            if isinstance(transformation[1],str):
                proposed_python = re.sub(transformation[0],transformation[1],proposed_python)
            else:
                for x in re.findall(transformation[0],proposed_python):
                    if '.' in(x):
                        proposed_python = proposed_python.replace(x,transformation[1](x))
        if lhs is not None:
            proposed_python = lhs + proposed_python
        return proposed_python

    def validateExpression (self,text):
        if text is None:
            return
        try:
            # this should work if we can just do a straight equality
            revised_text = self.patch_expression(text)
            ast.parse(revised_text)
            return revised_text,True
        except:
            try:
                revised_text = self.patch_expression(text, 's')
                ast.parse(revised_text)
                return revised_text[1:],False
            except:
                raise Exception("error parsing expression "+text)





    def eval_bmn_expression(self, inputExpr, matchExpr, **kwargs):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume it is equality.
        """
        if matchExpr is None:
            return True
        rhs, needsEquals = self.validateExpression(matchExpr)
        lhs, lhsNeedsEquals = self.validateExpression(inputExpr)
        if not lhsNeedsEquals:
            raise Exception("Input Expression '%s' is malformed"%inputExpr)
        if needsEquals:
           expression = lhs + ' == ' + rhs
        else:
            expression = lhs + rhs
        kwargs['convertTime'] = convertTime
        kwargs['FeelInterval'] = FeelInterval
        kwargs['FeelNot'] = FeelNot
        kwargs['Decimal'] = Decimal

        return self.evaluate(default_header + expression, **kwargs)

    def evaluate(self, expression, **kwargs):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        return self._eval(expression, **kwargs)

    def execute(self, task, script, **kwargs):
        """
        Execute the script, within the context of the specified task
        """
        locals().update(kwargs)
        locals().update({'task':task})
        exec(script)

    def _eval(self, expression, **kwargs):
        locals().update(kwargs)
        return eval(expression)
