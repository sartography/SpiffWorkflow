# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow.bpmn.BpmnScriptEngine import BpmnScriptEngine
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class SubWorkflowMultiTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('sub_workflow_multi1.bpmn', 'ScriptTest')

    def testRunThroughHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()


        print(self.workflow.is_completed())
        data = self.workflow.last_task.data

        print(data)
        self.assertEqual(data['c1'], 'HELLO')
        self.assertEqual(data['c2'], 'GOODBYE')




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SubWorkflowMultiTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
