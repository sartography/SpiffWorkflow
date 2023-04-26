# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.bpmn.FeelLikeScriptEngine import FeelLikeScriptEngine, FeelInterval
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import BoxedTaskDataEnvironment
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
import datetime

__author__ = 'matth'


class FeelExpressionTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.expressionEngine = FeelLikeScriptEngine(environment=BoxedTaskDataEnvironment())

    def testRunThroughExpressions(self):
        tests = [("string length('abcd')", 4, {}),
                 ("contains('abcXYZdef','XYZ')", True, {}),
                 ("list  contains(x,'b')", True, {'x': ['a', 'b', 'c']}),
                 ("list  contains(x,'z')", False, {'x': ['a', 'b', 'c']}),
                 # ("list contains(['a','b','c'],'b')",True,{}), # fails due to parse error
                 ("all ([True,True,True])", True, {}),
                 ("all ([True,False,True])", False, {}),
                 ("any ([False,False,False])", False, {}),
                 ("any ([True,False,True])", True, {}),
                 ("PT3S", datetime.timedelta(seconds=3), {}),
                 ("d[item>1]",[2,3,4],{'d':[1,2,3,4]}),
                 ("d[x>=2].y",[2,3,4],{'d':[{'x':1,'y':1},
                                           {'x': 2, 'y': 2},
                                           {'x': 3, 'y': 3},
                                           {'x': 4, 'y': 4},
                                            ]}),
                 ("concatenate(a,b,c)", ['a', 'b', 'c'], {'a': ['a'],
                                                          'b': ['b'],
                                                          'c': ['c'],
                                                          }),
                 ("append(a,'c')", ['a', 'b', 'c'], {'a': ['a', 'b']}),
                 ("now()", FeelInterval(datetime.datetime.now() - datetime.timedelta(seconds=1),
                                        datetime.datetime.now() + datetime.timedelta(seconds=1)),
                  {}),
                 ("day of week('2020-05-07')", 4, {}),
                 ("day of week(a)", 0, {'a': datetime.datetime(2020, 5, 3)}),
                 ("list contains(a.b,'x')", True, {'a': {'b': ['a', 'x']}}),  # combo
                 ("list contains(a.b,'c')", False, {'a': {'b': ['a', 'x']}}),
                 ("list contains(a.keys(),'b')", True, {'a': {'b': ['a', 'x']}}),
                 ("list contains(a.keys(),'c')", False, {'a': {'b': ['a', 'x']}}),
                 ]
        for test in tests:
            self.assertEqual(self.expressionEngine._evaluate(test[0], test[2]),
                             test[1], "test --> %s <-- with variables ==> %s <==Fail!" % (test[0], str(test[2])))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelExpressionTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
