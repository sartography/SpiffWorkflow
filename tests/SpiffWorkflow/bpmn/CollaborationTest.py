from SpiffWorkflow.bpmn.specs.SubWorkflowTask import CallActivity
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class CollaborationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('collaboration.bpmn', 'process_buddy')

    def testParseMessageFlow(self):

        self.assertDictEqual({'lover': ['lover_name']}, self.spec.correlation_keys)
        self.assertEqual(len(self.spec.outgoing_message_flows), 1)
        self.assertEqual(len(self.spec.incoming_message_flows), 1)
        outgoing, incoming = self.spec.outgoing_message_flows[0], self.spec.incoming_message_flows[0]

        self.assertEqual(outgoing.name, 'love_letter_flow')
        self.assertEqual(outgoing.message_ref, 'love_letter')
        self.assertEqual(outgoing.source_process, 'process_buddy')
        self.assertEqual(outgoing.source_task, 'ActivitySendLetter')
        self.assertEqual(outgoing.target_process, 'random_person_process')
        self.assertEqual(outgoing.target_task, None)

        love_letter = self.spec.task_specs[outgoing.source_task].event_definition
        self.assertEqual(len(love_letter.correlation_properties), 1)
        prop = love_letter.correlation_properties[0]
        self.assertEqual(prop.name, 'lover_name')
        self.assertEqual(prop.expression, 'lover_name')
        self.assertListEqual(prop.correlation_keys, ['lover'])

        self.assertEqual(incoming.name, 'response_flow')
        self.assertEqual(incoming.message_ref, 'love_letter_response')
        self.assertEqual(incoming.source_process, 'random_person_process')
        self.assertEqual(incoming.source_task, None)
        self.assertEqual(incoming.target_process, 'process_buddy')
        self.assertEqual(incoming.target_task, 'EventReceiveLetter')

        response = self.spec.task_specs[incoming.target_task].event_definition
        self.assertEqual(len(response.correlation_properties), 1)
        prop = response.correlation_properties[0]
        self.assertEqual(prop.name, 'lover_name')
        self.assertEqual(prop.expression, 'from_name')
        self.assertListEqual(prop.correlation_keys, ['lover'])

    def testParseCollaboration(self):

        spec, subprocesses = self.load_collaboration('collaboration.bpmn', 'my_collaboration')
        
        # Only executable processes should be started
        self.assertIn('process_buddy', subprocesses)
        self.assertNotIn('random_person_process', subprocesses)
        self.workflow = BpmnWorkflow(spec, subprocesses)
        start = self.workflow.get_tasks_from_spec_name('Start')[0]
        # Set up some data to be evaluated so that the workflow can proceed
        start.data['lover_name'] = 'Peggy'
        self.workflow.do_engine_steps()

        # Call activities should be created for executable processes and be reachable
        buddy = self.workflow.get_tasks_from_spec_name('process_buddy')[0]
        self.assertIsInstance(buddy.task_spec, CallActivity)
        self.assertEqual(buddy.task_spec.spec, 'process_buddy')
        self.assertEqual(buddy.state, TaskState.WAITING)

    def testSerialization(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()