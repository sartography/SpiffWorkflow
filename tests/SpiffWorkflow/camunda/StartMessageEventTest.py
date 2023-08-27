from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseTestCase import BaseTestCase

__author__ = 'kellym'


class StartMessageTest(BaseTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('message_test.bpmn', 'ThrowCatch')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

    def testParserCanReturnStartMessages(self):
        parser = self.get_parser('message_test.bpmn')
        self.assertEqual(
            parser.process_parsers['ThrowCatch'].start_messages(), ['ApprovalRequest'])

        parser = self.get_parser('random_fact.bpmn')
        self.assertEqual(
            parser.process_parsers['random_fact'].start_messages(), [])


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
                 ('Activity_EnablePlan',{'Done':'OK!'})]
        self.workflow.do_engine_steps() # get around start task
        ready_tasks = self.workflow.get_tasks(task_filter=self.ready_task_filter)
        waiting_tasks = self.workflow.get_tasks(task_filter=self.waiting_task_filter)
        self.assertEqual(1, len(ready_tasks),'Expected to have one ready task')
        self.assertEqual(1, len(waiting_tasks), 'Expected to have one waiting task')

        for step in steps:
            current_task = ready_tasks[0]
            self.assertEqual(current_task.task_spec.name,step[0])
            current_task.update_data(step[1])
            current_task.run()
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            if save_restore:
                self.save_restore()
            ready_tasks = self.workflow.get_tasks(task_filter=self.ready_task_filter)

        self.assertEqual(self.workflow.is_completed(),True,'Expected the workflow to be complete at this point')
        self.assertEqual(self.workflow.last_task.data,
            {
                'plan_details': 'Best',
                'ApprovalResult': 'Yes',
                'Done': 'OK!'
            })
