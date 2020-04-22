# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.exceptions import WorkflowException
__author__ = 'kellym'

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class ResetTokenTestMI(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/token_trial_MI.bpmn',
            'token')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)




    def actual_test(self, save_restore=False,reset_data=False):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        firsttaskid = None
        steps = [{'taskname':'First',
                  'formvar': 'First',
                  'answer': 'Yes'},
                 {'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'x'},
                 {'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'y'},
                 {'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'z'},

                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            if firsttaskid == None and step['taskname']=='FormA':
                firsttaskid = task.id
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.workflow.reset_task_from_id(firsttaskid)

        steps = [{'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'a1'},
                 {'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'a2'},
                 {'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'a3'},
                 {'taskname': 'FormC',
                  'formvar': 'C',
                  'answer': 'c'},
                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertTrue(self.workflow.is_completed())

        self.assertEqual({'current': 3, 'First': 'Yes', 'A': 'a3', 'output': {1: {'A': 'a1'}, 2: {'A': 'a2'},
                                                                               3: {'A': 'a3'}}, 'C': 'c'},
                         self.workflow.last_task.data)








def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenTestMI)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
