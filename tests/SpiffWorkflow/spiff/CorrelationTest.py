from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class CorrelationTest(BaseTestCase):

    def setUp(self):
        spec, subprocesses = self.load_collaboration('correlation_test.bpmn', 'plan')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testMessagePayload(self):

        plan_details = [ 'Plan A', 'Plan B', 'Plan C']
        self.workflow.do_engine_steps()

        for request_num in range(2):
            ready_tasks = self.workflow.get_ready_user_tasks()
            self.assertEqual(len(ready_tasks), 1)
            self.assertEqual(ready_tasks[0].task_spec.name, 'enter_plan')
            ready_tasks[0].data.update({
                'plan_details': plan_details[request_num], 
                'request_num': request_num
            })
            ready_tasks[0].complete()
            self.workflow.do_engine_steps()
            ready_tasks = self.workflow.get_ready_user_tasks()
            self.assertEqual(len(ready_tasks), 1)
            self.assertEqual(ready_tasks[0].task_spec.name, 'approve_or_deny')
            ready_tasks[0].data.update({ 'approved': ready_tasks[0].data['approval_request']['request_num'] == 1 })
            ready_tasks[0].complete()
            self.workflow.do_engine_steps()

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'execute_plan')
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        # Final plan details should reflect the accepted plan.
        self.assertEqual(self.workflow.data['plan_details'], 'Plan B')

    def testCorrelation(self):
        pass
