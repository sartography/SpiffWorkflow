# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonSriptEngine,FeelInterval
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
import datetime
__author__ = 'matth'


class PythonExpressionTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task with a loop cardinality of 5.
    It should repeat 5 times before termination."""

    def setUp(self):
        self.expressionEngine = PythonSriptEngine()


    def testRunThroughExpressions(self):
        tests = [("string length('abcd')",4,{}),
                 ("contains('abcXYZdef','XYZ')",True,{}),
                 ("list  contains(x,'b')",True,{'x':['a','b','c']}),
                 ("list  contains(x,'z')", False,{'x':['a','b','c']}),
                 #("list contains(['a','b','c'],'b')",True,{}), # fails due to parse error
                 ("all ([True,True,True])", True, {}),
                 ("all ([True,False,True])", False, {}),
                 ("any ([False,False,False])", False, {}),
                 ("any ([True,False,True])", True, {}),
                 ("concatenate(a,b,c)",['a','b','c'],{'a':['a'],
                                                      'b': ['b'],
                                                      'c': ['c'],
                                                      }),
                 ("append(a,'c')",['a','b','c'],{'a':['a','b']}),
                 ("now()",FeelInterval(datetime.datetime.now()-datetime.timedelta(seconds = 1),
                                       datetime.datetime.now() + datetime.timedelta(seconds=1)),
                  {}),
                 ("day of week('2020-05-07')",4,{}),
                 ("day of week(a)",0,{'a':datetime.datetime(2020,5,3)}),

                 ]
        for test in tests:
            self.assertEqual(self.expressionEngine.evaluate(test[0],**test[2]),
                  test[1],"test --> %s <-- with variables ==> %s <==Fail!"%(test[0],str(test[2])))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PythonExpressionTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
