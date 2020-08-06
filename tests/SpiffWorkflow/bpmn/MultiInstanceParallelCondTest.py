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


class MultiInstanceCondTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task set to be a parallel
    multi-instance with a loop cardinality of 5.
    It should repeat 5 times before termination, and it should
    have a navigation list with 7 items in it - one for start, one for end,
    and five items for the repeating section. """

    def setUp(self):
        self.filename = 'MultiInstanceParallelTaskCond.bpmn'
        self.process_name = 'MultiInstance'
        self.spec = self.load_workflow1_spec()


    def reload_save_restore(self):
        state = self._get_workflow_state()
        self.spec = self.load_workflow1_spec()
        self.workflow = BpmnWorkflow(self.spec)
        self.restore(state)
        # We should still have the same state:
        after_state = self._get_workflow_state(do_steps=False)
        self.maxDiff = None
        #self.assertEqual(before_dump, after_dump)
        self.assertEqual(state, after_state)



    def load_workflow1_spec(self):
        return self.load_workflow_spec(self.filename, self.process_name)

    def testRunThroughHappy(self):
        self.actualTest()

    def testSaveRestore(self):
        self.actualTest(True)

    def actualTest(self, save_restore=False):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_ready_user_tasks()))
        task = self.workflow.get_ready_user_tasks()[0]
        task.data['collection'] = {'a':{'a':'test'}}
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()

        for task in self.workflow.get_ready_user_tasks():
            self.assertFalse(self.workflow.is_completed())
            self.workflow.complete_task_from_id(task.id)
            nav_list = self.workflow.get_nav_list()
            self.assertEqual(3, len(nav_list))
            self.assertNotEqual(None, nav_list[2]['task_id'])
            if(save_restore):
                self.reload_save_restore()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceCondTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
