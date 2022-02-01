# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest

from SpiffWorkflow.bpmn.FunctionScriptEngine import FunctionScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'dkniep'


class FunctionScriptEngineTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.functionscriptEngine = FunctionScriptEngine(
            pythonpackage='tests.SpiffWorkflow.bpmn.FunctionScriptEngineTest')

        # All this, just so we have a task object, not using anything in the Script.
        spec = self.load_workflow_spec('FuncTest.bpmn', 'FuncTest')
        self.workflow = BpmnWorkflow(spec,
                                     script_engine=self.functionscriptEngine)
        self.workflow.data = {'scalar1': 1, 'testlist': [1, 2]}

    def testFunc(self):
        """Assure that we can run a function from the pythonpath"""
        self.workflow.do_engine_steps()
        self.task = self.workflow.last_task
        self.assertEqual(self.task.data['flipflap'], 4)
        self.assertEqual(self.task.workflow.data,
                         {'scalar1': 12, 'testlist': [1, 2, 3, 4], 't1': 'bla',
                          'flipflap': 4, 'end_event': None})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(
        FunctionScriptEngineTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())


def testfunc1(taskdata, workflowdata, extensions):
    """
    Function to be run by the script
    :param extensions:
    :return:
    """
    taskdata['flipflap'] = 2
    workflowdata['testlist'].append(3)
    workflowdata.update(extensions)


def testfunc2(taskdata, workflowdata, extensions):
    """
    Function to be run by the script
    :param extensions:
    :return:
    """
    taskdata['flipflap'] = 4
    workflowdata['testlist'].append(4)
    workflowdata['scalar1'] = 12
