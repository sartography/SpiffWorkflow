import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class CorrelationTest(BaseTestCase):

    def testMessagePayload(self):
        self.actual_test(False)

    def testMessagePayloadSaveRestore(self):
        self.actual_test(True)

    def actual_test(self,save_restore):

        specs = self.get_all_specs('correlation.bpmn')
        proc_1 = specs['proc_1']
        self.workflow = BpmnWorkflow(proc_1, specs)
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()
        # Set up some data to evaluate the payload expression against
        for idx, task in enumerate(self.workflow.get_ready_user_tasks()):
            task.data['task_num'] = idx
            task.data['task_name'] = f'subprocess {idx}'
            task.data['extra_data'] = f'unused data'
            task.complete()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        for task in ready_tasks:
            self.assertEqual(task.task_spec.name, 'prepare_response')
            response = 'OK' if task.data['source_task']['num'] else 'No'
            task.data.update(response=response)
            task.complete()
        self.workflow.do_engine_steps()
        # If the messages were routed properly, the task number should match the response id
        for task in self.workflow.get_tasks_from_spec_name('subprocess_end'):
            self.assertEqual(task.data['response']['init_id'], task.data['task_num'])
            self.assertEqual(task.data['response']['response'], 'OK' if task.data['task_num'] else 'No')


class DualConversationTest(BaseTestCase):

    def testTwoCorrelatonKeys(self):

        spec, subprocesses = self.load_workflow_spec('correlation_two_conversations.bpmn', 'message_send_process')
        workflow = BpmnWorkflow(spec, subprocesses)
        workflow.do_engine_steps()
        messages = workflow.get_bpmn_messages()
        self.assertEqual(len(messages), 2)
        message_one = [ msg for msg in messages if msg.name== 'Message Send One' ][0]
        message_two = [ msg for msg in messages if msg.name== 'Message Send Two' ][0]
        self.assertIn('message_correlation_key_one', message_one.correlations)
        self.assertNotIn('message_correlation_key_one', message_two.correlations)
        self.assertIn('message_correlation_key_two', message_two.correlations)
        self.assertNotIn('message_correlation_key_two', message_one.correlations)
