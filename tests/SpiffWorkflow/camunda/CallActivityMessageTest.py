import unittest

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseTestCase import BaseTestCase

__author__ = 'essweine'


class CallActivityMessageTest(BaseTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('call_activity_with_message*.bpmn', 'Process_0xeaemr')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):
        steps = [('Activity_EnterPlan',{'plan_details':'Bad'}),
                 ('Activity_ApproveOrDeny', {'approved':'No'}),
                 ('Activity_EnterPlan', {'plan_details':'Better'}),
                 ('Activity_ApproveOrDeny', {'approved':'No'}),
                 ('Activity_EnterPlan', {'plan_details':'Best'}),
                 ('Activity_ApproveOrDeny', {'approved':'Yes'}),
                 ('Activity_EnablePlan',{'Done':'OK!'})
                 ]

        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        waiting_tasks = self.workflow.get_tasks(TaskState.WAITING)
        self.assertEqual(1, len(ready_tasks),'Expected to have one ready task')
        self.assertEqual(2, len(waiting_tasks), 'Expected to have two waiting tasks')

        for step in steps:
            current_task = ready_tasks[0]
            self.assertEqual(current_task.task_spec.name,step[0])
            current_task.update_data(step[1])
            current_task.complete()
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            if save_restore: self.save_restore()
            ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(self.workflow.is_completed(),True,'Expected the workflow to be complete at this point')
        self.assertEqual(self.workflow.last_task.data,{'plan_details': 'Best',
                                                       'Approved': 'Yes',
                                                       'Done': 'OK!'})



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CallActivityMessageTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
