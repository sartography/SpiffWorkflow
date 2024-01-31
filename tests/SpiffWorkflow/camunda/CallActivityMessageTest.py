from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from .BaseTestCase import BaseTestCase

__author__ = 'essweine'


class CallActivityMessageTest(BaseTestCase):

    def setUp(self):
        spec, subprocesses = self.load_collaboration('call_activity_with_message*.bpmn', 'Parent_Process')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):
        steps = [
            ('Activity_EnterPlan',{'plan_details':'Bad'}),
            ('Activity_ApproveOrDeny', {'approved':'No'}),
            ('Activity_EnterPlan', {'plan_details':'Better'}),
            ('Activity_ApproveOrDeny', {'approved':'No'}),
            ('Activity_EnterPlan', {'plan_details':'Best'}),
            ('Activity_ApproveOrDeny', {'approved':'Yes'}),
            ('Activity_EnablePlan',{'Done':'OK!'})
         ]

        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        waiting_tasks = self.workflow.get_tasks(state=TaskState.WAITING)
        self.assertEqual(1, len(ready_tasks),'Expected to have one ready task')
        self.assertEqual(2, len(waiting_tasks), 'Expected to have two waiting tasks')

        for step in steps:
            current_task = ready_tasks[0]
            self.assertEqual(current_task.task_spec.name, step[0])
            current_task.set_data(**step[1])
            current_task.run()
            self.workflow.do_engine_steps()
            if save_restore:
                self.save_restore()
            ready_tasks = self.workflow.get_tasks(state=TaskState.READY)

        self.assertEqual(self.workflow.is_completed(), True, 'Expected the workflow to be complete at this point')
        self.assertEqual(
            self.workflow.last_task.data,
            {'plan_details': 'Best', 'Approved': 'Yes', 'Done': 'OK!'}
        )
