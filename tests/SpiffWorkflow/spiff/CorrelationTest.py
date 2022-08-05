from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class CorrelationTest(BaseTestCase):

    def setUp(self):
        spec, subprocesses = self.load_collaboration('correlation_test.bpmn', 'plan')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.plan_details = [ 'Plan A', 'Plan B', 'Plan C']

    def testMessagePayload(self):

        self.workflow.do_engine_steps()
        self.request_approval(0, False)
        self.request_approval(1, True)
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'execute_plan')
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        # Final plan details should reflect the accepted plan.
        self.assertEqual(self.workflow.data['plan_details'], 'Plan B')

    def testCorrelation(self):

        self.workflow.do_engine_steps()
        self.request_approval(0, False)
        self.request_approval(1, False)
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(ready_tasks[0].task_spec.name, 'enter_plan')
        ready_tasks[0].data.update({'justification': 'This plan is awesome.'})
        self.request_approval(2, False)
        self.workflow.do_engine_steps()
        # This time we asked for an appeal, so there should be one external message waiting
        messages = self.workflow.get_bpmn_messages()
        self.assertEqual(len(messages), 1)
        self.assertDictEqual(messages[0].correlations, {'request': {'request_num': 2}})
        self.assertEqual(messages[0].payload.name, 'appeal')
        self.assertEqual(messages[0].message_flows[0].message_ref, 'appeal')
        # The workflow message queue should be clear now
        self.assertEqual(len(self.workflow.bpmn_messages), 0)

    def request_approval(self, request_num, approve):

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'enter_plan')
        ready_tasks[0].data.update({
            'plan_details': self.plan_details[request_num], 
            'request_num': request_num
        })
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'approve_or_deny')
        ready_tasks[0].data.update({ 'approved': approve })
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()