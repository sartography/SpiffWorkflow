# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
import datetime
import time
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class ExternalMessageBoundaryTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('external_message.bpmn', 'ExternalMessage')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)



    def actual_test(self,save_restore = False):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(1, len(ready_tasks),'Expected to have only one ready task')
        self.workflow.message('Interrupt','SomethingImportant','interrupt_var')
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(2,len(ready_tasks),'Expected to have only one ready task')
        # here because the thread just dies and doesn't lead to a task, we expect the data
        # to die with it.
        # item 1 should be at 'Pause'
        self.assertEqual('Pause',ready_tasks[1].task_spec.description)
        self.assertEqual('SomethingImportant', ready_tasks[1].data['interrupt_var'])
        self.assertEqual(True, ready_tasks[1].data['caughtinterrupt'])
        self.assertEqual('Meaningless User Task',ready_tasks[0].task_spec.description)
        self.assertEqual(False, ready_tasks[0].data['caughtinterrupt'])
        self.workflow.complete_task_from_id(ready_tasks[1].id)
        self.workflow.do_engine_steps()
        # what I think is going on here is that when we hit the reset, it is updating the
        # last_task and appending the data to whatever happened there, so it would make sense that
        # we have the extra variables that happened in 'pause'
        # if on the other hand, we went on from 'meaningless task' those variables would not get added.
        self.workflow.message('reset','SomethingDrastic','reset_var')
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(1, len(ready_tasks),'Expected to have only one ready task')
        self.assertEqual('SomethingDrastic', ready_tasks[0].data['reset_var'])
        self.assertEqual(False, ready_tasks[0].data['caughtinterrupt'])

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExternalMessageBoundaryTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
