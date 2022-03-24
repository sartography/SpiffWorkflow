# -*- coding: utf-8 -*-



import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class SubWorkflowMultiTest(BpmnWorkflowTestCase):

    expected_data = {
     'a': {'name': 'Apple_edit',
           'new_info': 'Adding this!'},
     'b': {'name': 'Bubble_edit',
           'new_info': 'Adding this!'},
     'c': {'name': 'Crap, I should write better code_edit',
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

    def testWrapped(self):
        self.spec = self.load_workflow_spec('sub_within_sub_multi.bpmn', 'ScriptTest')
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        data = self.workflow.last_task.data
        self.assertEqual(self.expected_data, data['my_collection'])



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SubWorkflowMultiTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
