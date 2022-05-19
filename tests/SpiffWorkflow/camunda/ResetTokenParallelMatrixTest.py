# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase

__author__ = 'kellym'

class ResetTokenTestParallelMatrix(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('token_trial_parallel_matrix.bpmn', 'token')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def testRunThroughHappyAlt(self):
        self.actual_test2(save_restore=False)

    def testRunThroughSaveRestoreAlt(self):
        self.actual_test2(save_restore=True)



    def actual_test(self, save_restore=False,reset_data=False):
        """
        Test a complicated parallel matrix, complete the matrix and
        Reset somewhere in the middle. It should complete the row that we
        Reset to, and retain all previous answers.
        """
        
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

        self.assertEqual({'First': 'Yes',
                          'A1': 'xa1',
                          'A2': 'xa2',
                          'A3': 'xa3',
                          'B1': 'xb1',
                          'B2': 'b2',
                          'B3': 'b3',
                          'C1': 'xc1',
                          'C2': 'xc2',
                          'C3': 'xc3',
                          'D': 'd'},

                          self.workflow.last_task.data)


    def actual_test2(self, save_restore=False,reset_data=False):
        """
        Test a complicated parallel matrix,
        Complete several items in the parallel matrix, but do not complete it,
        Reset to a previous version on another branch of the parallel, it should
        complete that branch and then pick up where we left off.
        Also, after we reset the branch, there should then be three tasks ready,
        A2,B3,and C1
        """
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

                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            if firsttaskid == None and step['taskname']=='FormA2':
                firsttaskid = task.id
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.workflow.reset_task_from_id(firsttaskid)
        #NB - this won't test random access
        steps = [{'taskname': 'FormA2',
                  'formvar': 'A2',
                  'answer': 'a2'},
                 {'taskname': 'FormA3',
                  'formvar': 'A3',
                   'answer': 'a3'},

                 {'taskname': 'FormB3',
                  'formvar': 'B3',
                  'answer': 'b3'},
                 {'taskname': 'FormC1',
                  'formvar': 'C1',
                  'answer': 'c1'},
                 {'taskname': 'FormC2',
                  'formvar': 'C2',
                  'answer': 'c2'},
                 {'taskname': 'FormC3',
                  'formvar': 'C3',
                  'answer': 'c3'},

                 {'taskname': 'FormD',
                  'formvar': 'D',
                  'answer': 'd'},
                 ]
        readytasks = [t.task_spec.name for t in self.workflow.get_ready_user_tasks()]
        self.assertEqual(readytasks,['FormA2','FormB3','FormC1'])
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertTrue(self.workflow.is_completed())

        self.assertEqual({'First': 'Yes',
                          'A1': 'xa1',
                          'A2': 'a2',
                          'A3': 'a3',
                          'B1': 'xb1',
                          'B2': 'xb2',
                          'B3': 'b3',
                          'C1': 'c1',
                          'C2': 'c2',
                          'C3': 'c3',
                          'D': 'd'},

                          self.workflow.last_task.data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenTestParallelMatrix)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
