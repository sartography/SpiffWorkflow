# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class SubWorkflowMultiTest(BpmnWorkflowTestCase):

    expected_data = {
     'a': {'name': 'Apple',
           'new_info': 'Adding this!'},
     'b': {'name': 'Bubble',
           'new_info': 'Adding this!'},
     'c': {'name': 'Crap, I should write better code',
           'new_info': 'Adding this!'}
    }

    def testSequential(self):
        self.spec = self.load_workflow_spec('sub_workflow_multi.bpmn', 'ScriptTest')
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        data = self.workflow.last_task.data
        self.assertEqual(data['my_collection'], self.expected_data)

    def testParallel(self):
        self.spec = self.load_workflow_spec('sub_workflow_multi_parallel.bpmn', 'ScriptTest')
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        data = self.workflow.last_task.data
        self.assertEqual(data['my_collection'], self.expected_data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SubWorkflowMultiTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
