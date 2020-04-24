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


class ResetTokenTestParallelMatrix(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/token_trial_parallel_matrix.bpmn',
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
                 {'taskname': 'FormA1',
                  'formvar': 'A1',
                  'answer': 'xa1'},
                 {'taskname': 'FormA2',
                  'formvar': 'A2',
                  'answer': 'xa2'},
                 {'taskname': 'FormA3',
                  'formvar': 'A3',
                  'answer': 'xa3'},
                 {'taskname': 'FormB1',
                  'formvar': 'B1',
                  'answer': 'xb1'},
                 {'taskname': 'FormB2',
                  'formvar': 'B2',
                  'answer': 'xb2'},
                 {'taskname': 'FormB3',
                  'formvar': 'B3',
                  'answer': 'xb3'},
                 {'taskname': 'FormC1',
                  'formvar': 'C1',
                  'answer': 'xc1'},
                 {'taskname': 'FormC2',
                  'formvar': 'C2',
                  'answer': 'xc2'},
                 {'taskname': 'FormC3',
                  'formvar': 'C3',
                  'answer': 'xc3'},

                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            if firsttaskid == None and step['taskname']=='FormB2':
                firsttaskid = task.id
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.workflow.reset_task_from_id(firsttaskid)
        #NB - this won't test random access
        steps = [{'taskname': 'FormB2',
                  'formvar': 'B2',
                  'answer': 'b2'},
                 {'taskname': 'FormB3',
                  'formvar': 'B3',
                  'answer': 'b3'},
                 {'taskname': 'FormD',
                  'formvar': 'D',
                  'answer': 'd'},
                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertTrue(self.workflow.is_completed())

        self.assertEqual({'current': 3,
                          'First': 'Yes',
                          'A1': 'xa1',
                          'A2': 'xa2',
                          'A3': 'xa3',
                          'B1': 'xb1',
                          'B2': 'b2',
                          'B3': 'b3',
                          'C1': 'xa1',
                          'C2': 'xa1',
                          'C3': 'xa1',
                          'D': 'd'}

                          self.workflow.last_task.data)








def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenTestParallelMatrix)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())C