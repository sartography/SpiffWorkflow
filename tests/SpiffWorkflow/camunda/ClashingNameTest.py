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


class ClashingNameTest(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/token_trial_camunda_clash.bpmn',
            'token')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def testRunThroughHappyReset(self):
        self.actual_test(save_restore=False,reset_data=True,expected={'do_step':False,'C':'c'})

    def testRunThroughSaveRestoreReset(self):
        self.actual_test(save_restore=True,reset_data=True,expected={'do_step':False,'C':'c'})



    def actual_test(self, save_restore=False,reset_data=False,expected={'do_step':False,'A':'a','B':'b','C':'c'}):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        firsttaskid = None
        steps = [{'taskname':'First',
                  'formvar': 'do_step',
                  'answer': True},
                 {'taskname': 'FormA',
                  'formvar': 'A',
                  'answer': 'a'},
                 {'taskname': 'FormB',
                  'formvar': 'B',
                  'answer': 'b'},
                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            if firsttaskid == None:
                firsttaskid = task.id
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data({step['formvar']: step['answer']})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.workflow.reset_task_from_id(firsttaskid)
        steps = [{'taskname':'First',
                  'formvar': 'do_step',
                  'answer': False},
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

        self.assertEqual({'do_step':False,'A':'a','B':'b','C':'c'},
                         self.workflow.last_task.data)








def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ClashingNameTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
