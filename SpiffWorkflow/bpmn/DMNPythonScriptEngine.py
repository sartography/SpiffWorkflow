# -*- coding: utf-8 -*-
from builtins import object
import ast
import re
import operator
import datetime
from datetime import timedelta
from decimal import Decimal
from SpiffWorkflow.workflow import WorkflowException
from .PythonScriptEngine import PythonScriptEngine, Box

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

class DMNPythonScriptEngine(PythonScriptEngine):
    """
    This simply overrides the python script engine to do some specific things for
    DMN - I left the underlying PythonScriptEngine with everything in place so it
    will play nice with the existing FeelLikeScriptEngine
    """
    def __init__(self):
        super().__init__()

    def eval_dmn_expression(self, inputExpr, matchExpr, **kwargs):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume it is equality.
        """



        if matchExpr is None:
            return True

        nolhs = False
        if '?' in matchExpr:
            nolhs = True
            matchExpr = matchExpr.replace('?', 'dmninputexpr')

        rhs, needsEquals = self.validateExpression(matchExpr)

        extra = {
            'datetime': datetime,
            'timedelta': timedelta,
            'Decimal': Decimal,
            'Box': Box
        }

        lhs, lhsNeedsEquals = self.validateExpression(inputExpr)
        if not lhsNeedsEquals:
            raise WorkflowException("Input Expression '%s' is malformed"%inputExpr)
        if nolhs:
            dmninputexpr = self.evaluate(lhs, external_methods= extra, **kwargs)
            extra = {'dmninputexpr':dmninputexpr,
                     'datetime':datetime,
                     'timedelta':timedelta,
                     'Decimal':Decimal,
                     'Box':Box
            }
            return self.evaluate(rhs,external_methods=extra, **kwargs)
        if needsEquals:
           expression = lhs + ' == ' + rhs
        else:
            expression = lhs + rhs

        return self.evaluate(expression, external_methods=extra, **kwargs)

