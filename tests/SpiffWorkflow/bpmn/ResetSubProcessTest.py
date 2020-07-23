# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ResetSubProcessTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task set to be a parallel
    multi-instance with a loop cardinality of 5.
    It should repeat 5 times before termination, and it should
    have a navigation list with 7 items in it - one for start, one for end,
    and five items for the repeating section. """

    def setUp(self):
        self.filename = 'resetworkflowA-*.bpmn'
        self.process_name = 'TopLevel'
        self.spec = self.load_workflow1_spec()


    def reload_save_restore(self):
        self.filename = 'resetworkflowB-*.bpmn'
        self.spec = self.load_workflow1_spec()
        self.workflow.do_engine_steps()
        self.save_restore()

    def load_workflow1_spec(self):
        return self.load_workflow_spec(self.filename, self.process_name)

    def testSaveRestore(self):
        self.actualTest(True)

    def actualTest(self, save_restore=False):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_ready_user_tasks()))
        task = self.workflow.get_ready_user_tasks()[0]
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        navlist = self.workflow.get_nav_list()
        self.assertEqual(len(navlist),3)
        self.assertEqual(navlist[1]['name'],'SubTask2')
        self.assertEqual(navlist[1]['state'], 'READY')
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'SubTask2')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_tasks_from_spec_name('Task1')[0]
        task.reset_token()
        self.workflow.do_engine_steps()
        self.reload_save_restore()
        task = self.workflow.get_ready_user_tasks()[0]
        navlist = self.workflow.get_nav_list()
        self.assertEqual(len(navlist), 4)
        self.assertEqual(navlist[1]['name'], 'Subtask2')

        self.assertEqual(task.get_name(),'Task1')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'Subtask2')
        navlist = self.workflow.get_nav_list()
        self.assertEqual(len(navlist), 4)
        self.assertEqual(navlist[1]['state'], 'READY')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'Subtask2A')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'Task2')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetSubProcessTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
