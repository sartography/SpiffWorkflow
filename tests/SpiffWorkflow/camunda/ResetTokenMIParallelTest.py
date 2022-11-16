# -*- coding: utf-8 -*-

import unittest

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

__author__ = 'kellym'

class ResetTokenTestMIParallel(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('token_trial_MIParallel.bpmn', 'token')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False,reset_data=False):

        self.workflow.do_engine_steps()
        firsttaskid = None
        steps = [{'taskname':'First',
                  'task_data': {'do_step':'Yes'}},
                 {'taskname': 'FormA',
                  'task_data': {'current': {'A' : 'x'}}},
                 {'taskname': 'FormA',
                  'task_data': {'current': {'A' : 'y'}}},
                 {'taskname': 'FormA',
                  'task_data': {'current': {'A' : 'z'}}}
                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            if firsttaskid == None and step['taskname']=='FormA':
                firsttaskid = task.id
            self.assertEqual(step['taskname'], task.task_spec.name[:len(step['taskname'])])
            task.update_data(step['task_data'])
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertEqual({'do_step': 'Yes',
                          'output': {'1': {'A': 'x'}, '2': {'A': 'y'}, '3': {'A': 'z'}}},
                         self.workflow.last_task.data)

        self.workflow.reset_task_from_id(firsttaskid)
        #NB - this won't test random access
        steps = [{'taskname': 'FormA',
                  'task_data': {'current': {'A' : 'a1'}}},
                 {'taskname': 'FormC',
                  'task_data': {'C' : 'c'}},
                 ]
        for step in steps:
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEqual(step['taskname'], task.task_spec.name)
            task.update_data(step['task_data'])
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertTrue(self.workflow.is_completed())

        self.assertEqual({'do_step': 'Yes',
                          'C': 'c',
                          'output': {'1': {'A': 'a1'},
                                     '2': {'A': 'y'},
                                     '3': {'A': 'z'}}},
                         self.workflow.last_task.data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenTestMIParallel)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
