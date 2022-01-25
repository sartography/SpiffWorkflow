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


class StartMessageTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('message_test.bpmn', 'ThrowCatch')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)



    def actual_test(self,save_restore = False):
        steps = [('Activity_EnterPlan',{'plan_details':'Bad'}),
                 ('Activity_ApproveOrDeny', {'approved':'No'}),
                 ('Activity_EnterPlan', {'plan_details':'Better'}),
                 ('Activity_ApproveOrDeny', {'approved':'No'}),
                 ('Activity_EnterPlan', {'plan_details':'Best'}),
                 ('Activity_ApproveOrDeny', {'approved':'Yes'}),
                 ('Activity_EnablePlan',{'Done':'OK!'})
                 ]
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps() # get around start task
        ready_tasks = self.workflow.get_tasks(Task.READY)
        waiting_tasks = self.workflow.get_tasks(Task.WAITING)
        self.assertEqual(1, len(ready_tasks),'Expected to have one ready task')
        self.assertEqual(1, len(waiting_tasks), 'Expected to have one waiting task')

        for step in steps:
            current_task = ready_tasks[0]
            self.assertEqual(current_task.task_spec.name,step[0])
            current_task.update_data(step[1])
            current_task.complete()
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            if save_restore: self.save_restore()
            ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(self.workflow.is_completed(),True,'Expected the workflow to be complete at this point')
        self.assertEqual(self.workflow.last_task.data,{'plan_details': 'Best',
                                                       'ApprovalResult': 'Yes',
                                                       'Done': 'OK!'})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(StartMessageTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
