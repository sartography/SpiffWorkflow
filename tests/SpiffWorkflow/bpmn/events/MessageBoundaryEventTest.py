# -*- coding: utf-8 -*-



import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class MessageBoundaryTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('MessageBoundary.bpmn', 'MessageBoundary')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)



    def actual_test(self,save_restore = False):
        steps = [('Activity_Interrupt', {'interrupt_task':'No'}),
                 ('Activity_Interrupt', {'interrupt_task': 'No'}),
                 ('Activity_Interrupt', {'interrupt_task': 'Yes'}),
                 ]
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(2, len(ready_tasks),'Expected to have two ready tasks')
        for step in steps:
            for task in ready_tasks:
                if task.task_spec.name == step[0]:
                    task.update_data(step[1])

                self.workflow.complete_task_from_id(task.id)
                self.workflow.do_engine_steps()
                time.sleep(.1)
                self.workflow.refresh_waiting_tasks()
                if save_restore: self.save_restore()
            ready_tasks = self.workflow.get_tasks(TaskState.READY)
        time.sleep(.1)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(),True,'Expected the workflow to be complete at this point')



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessageBoundaryTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
