# -*- coding: utf-8 -*-

import re
import datetime
import operator
from datetime import timedelta
from decimal import Decimal
from .PythonScriptEngine import PythonScriptEngine

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


def feelConvertTime(datestr,parsestr):
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

def feelConcatenate(*lst):
    ilist = []
    for l in lst:
        ilist = ilist + l
    return ilist

def feelAppend(lst,item):
    newlist = lst[:]  # get a copy
    newlist.append(item)
    return newlist

def feelNow():
    return datetime.datetime.now()

def feelGregorianDOW(date):
    # we assume date is either date in Y-m-d format
    # or it is of datetime class
    if isinstance(date,str):
        date = datetime.datetime.strptime(date,'%Y-%m-%d')
    return date.isoweekday()%7


def transformDuration(duration,td):
    if duration:
        return td * float(duration)
    else:
        return timedelta(seconds=0)

def lookupPart(code,base):
    x= re.search("([0-9.]+)"+code,base)
    if x:
        return x.group(1)
    else:
        return None

def feelFilter(var,a,b,op,column=None):
    """
    here we are trying to cover some of the basic test cases,
    dict, list of dicts and list.
    """
    opmap = {'=':operator.eq,
             '<':operator.lt,
             '>':operator.gt,
             '<=':operator.le,
             '>=':operator.ge,
             '!=':operator.ne}
    b = eval(b)
    # if it is a list and we are referring to 'item' then we
    # expect the variable to be a simple list
    if (isinstance(var,list)) and a == 'item':
        return [x for x in var if opmap[op](x,b)]
    # if it is a dictionary, and the keys refer to dictionaries,
    # then we convert it to a list of dictionaries with the elements
    # all having {'key':key,<rest of dict>}
    # if it is a dictionary and the key refers to a non-dict, then
    # we convert to a dict having {'key':key,'value':value}
    if (isinstance(var,dict)):
        newvar = []
        for key in var.keys():
            if isinstance(var[key],dict):
                newterm = var[key]
                newterm.update({'key':key})
                newvar.append(newterm)
            else:
                newvar.append({'key':key,'value':var[key]})
        var = newvar

    if column!=None:
        return [x.get(column) for x in var if opmap[op](x.get(a), b)]
    else:
        return [x for x in var if opmap[op](x.get(a), b)]



def feelParseISODuration(input):
    """
    Given an ISO duration designation
    such as :
        P0Y1M2DT3H2S
    and convert it into a python timedelta

    Abbreviations may be made as in :

       PT30S

    NB:
    Months are defined as 30 days currently - as I am dreading getting into
    Date arithmetic edge cases.

    """
    if input[0] != 'P':
        raise Exception("Oh Crap!")
    input = input[1:]
    days, time = input.split("T")
    lookups = [("Y",days,timedelta(days=365)),
               ("M", days, timedelta(days=30)),
               ("W", days, timedelta(days=7)),
               ("D", days, timedelta(days=1)),
               ("H", time, timedelta(seconds=60*60)),
               ("M", time, timedelta(seconds=60)),
               ("S", time, timedelta(seconds=1)),
               ]
    totaltime = [transformDuration(lookupPart(x[0],x[1]),x[2]) for x in lookups]
    return sum(totaltime,timedelta(seconds=0))



# Order Matters!!
fixes = [(r'string\s+length\((.+?)\)','len(\\1)'),
         (r'count\((.+?)\)','len(\1)'),
         (r'concatenate\((.+?)\)','feelConcatenate(\\1)'),
         (r'append\((.+?),(.+?)\)','feelAppend(\\1,\\2)'), # again will not work with literal list
         (r'list\s+contains\((.+?),(.+?)\)','\\2 in \\1'), # list contains(['a','b','stupid,','c'],'stupid,') will break
         (r'contains\((.+?),(.+?)\)','\\2 in \\1'), # contains('my stupid, stupid comment','stupid') will break
         (r'not\s+?contains\((.+?)\)','FeelContains(\\1,invert=True)'), # not  contains('something')
         (r'not\((.+?)\)','FeelNot(\\1)'),   # not('x')

         (r'now\(\)','feelNow()'),
         (r'contains\((.+?)\)', 'FeelContains(\\1)'), # contains('x')
         # date  and time (<datestr>)
         (r'date\s+?and\s+?time\s*\((.+?)\)', 'feelConvertTime(\\1,"%Y-%m-%dT%H:%M:%S")'),
         (r'date\s*\((.+?)\)', 'feelConvertTime(\\1,"%Y-%m-%d)'),  # date (<datestring>)
         (r'day\s+of\s+\week\((.+?)\)','feelGregorianDOW(\\1)'),
         (r'\[([^\[\]]+?)[.]{2}([^\[\]]+?)\]','FeelInterval(\\1,\\2)'),                # closed interval on both sides
         (r'[\]\(]([^\[\]\(\)]+?)[.]{2}([^\[\]\)\(]+?)\]','FeelInterval(\\1,\\2,leftOpen=True)'),  # open lhs
         (r'\[([^\[\]\(\)]+?)[.]{2}([^\[\]\(\)]+?)[\[\)]','FeelInterval(\\1,\\2,rightOpen=True)'), # open rhs
         # I was having problems with this matching a "P" somewhere in another expression
         # so I added a bunch of different cases that should isolate this.
         (r'^(P(([0-9.]+Y)?([0-9.]+M)?([0-9.]+W)?([0-9.]+D)?)?(T([0-9.]+H)?([0-9.]+M)?([0-9.]+S)?)?)$',
          'feelParseISODuration("\\1")'), ## Parse ISO Duration convert to timedelta - standalone
         (r'^(P(([0-9.]+Y)?([0-9.]+M)?([0-9.]+W)?([0-9.]+D)?)?(T([0-9.]+H)?([0-9.]+M)?([0-9.]+S)?)?)\s',
          'feelParseISODuration("\\1") '),  ## Parse ISO Duration convert to timedelta beginning
         (r'\s(P(([0-9.]+Y)?([0-9.]+M)?([0-9.]+W)?([0-9.]+D)?)?(T([0-9.]+H)?([0-9.]+M)?([0-9.]+S)?)?)\s',
          ' feelParseISODuration("\\1") '),  ## Parse ISO Duration convert to timedelta in context
         (r'\s(P(([0-9.]+Y)?([0-9.]+M)?([0-9.]+W)?([0-9.]+D)?)?(T([0-9.]+H)?([0-9.]+M)?([0-9.]+S)?)?)$',
          ' feelParseISODuration("\\1")'),  ## Parse ISO Duration convert to timedelta end

         (r'(.+)\[(\S+)?(<=)(.+)]\.(\S+)', 'feelFilter(\\1,"\\2","\\4","\\3","\\5")'),  # implement a simple filter
         (r'(.+)\[(\S+)?(>=)(.+)]\.(\S+)', 'feelFilter(\\1,"\\2","\\4","\\3","\\5")'),  # implement a simple filter
         (r'(.+)\[(\S+)?(!=)(.+)]\.(\S+)', 'feelFilter(\\1,"\\2","\\4","\\3","\\5")'),  # implement a simple filter
         (r'(.+)\[(\S+)?([=<>])(.+)]\.(\S+)', 'feelFilter(\\1,"\\2",\\4,"\\3","\\5")'),  # implement a simple filter
         (r'(.+)\[(\S+)?(<=)(.+)]', 'feelFilter(\\1,"\\2","\\4","\\3")'),  # implement a simple filter
         (r'(.+)\[(\S+)?(>=)(.+)]', 'feelFilter(\\1,"\\2","\\4","\\3")'),  # implement a simple filter
         (r'(.+)\[(\S+)?(!=)(.+)]', 'feelFilter(\\1,"\\2","\\4","\\3")'),  # implement a simple filter
         (r'(.+)\[(\S+)?([=<>])(.+)]','feelFilter(\\1,"\\2","\\4","\\3")'), # implement a simple filter
         (r'[\]\(]([^\[\]\(\)]+?)[.]{2}([^\[\]\(\)]+?)[\[\)]',
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

         ('true','True'),
         ('false','False')
    ]
         
externalFuncs = {
    'feelConvertTime':feelConvertTime,
    'FeelInterval':FeelInterval,
    'FeelNot':FeelNot,
    'Decimal':Decimal,
    'feelConcatenate': feelConcatenate,
    'feelAppend': feelAppend,
    'feelFilter': feelFilter,
    'feelNow': feelNow,
    'FeelContains': FeelContains,
    'datetime':datetime,
    'feelParseISODuration': feelParseISODuration,
    'feelGregorianDOW':feelGregorianDOW,
}


class FeelLikeScriptEngine(PythonScriptEngine):
    """
    This should serve as a base for all scripting & expression evaluation
    operations that are done within both BPMN and BMN. Eventually it will also
    serve as a base for FEEL expressions as well

    If you are uncomfortable with the use of eval() and exec, then you should
    provide a specialised subclass that parses and executes the scripts /
    expressions in a mini-language of your own.
    """
    def __init__(self):
        super().__init__()

    def validate(self, expression):
        super().validate(self.patch_expression(expression))

    def patch_expression(self, invalid_python, lhs=''):
        if invalid_python is None:
            return None
        proposed_python = invalid_python
        for transformation in fixes:
            if isinstance(transformation[1], str):
                proposed_python = re.sub(transformation[0], transformation[1], proposed_python)
            else:
                for x in re.findall(transformation[0], proposed_python):
                    if '.' in(x):
                        proposed_python = proposed_python.replace(x, transformation[1](x))
        if lhs is not None:
            proposed_python = lhs + proposed_python
        return proposed_python

    def _evaluate(self, expression, context, task=None, external_methods=None):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.
        """
        if external_methods is None:
            external_methods = {}

        revised = self.patch_expression(expression)
        external_methods.update(externalFuncs)
        return super()._evaluate(revised, context, external_methods=external_methods)

    def execute(self, task, script, data, external_methods=None):
        """
        Execute the script, within the context of the specified task
        """
        if external_methods is None:
            external_methods = {}
        external_methods.update(externalFuncs)
        super(PythonScriptEngine).execute(task, script, external_methods)




