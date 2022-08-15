from SpiffWorkflow import workflow
from SpiffWorkflow.bpmn.specs.SubWorkflowTask import CallActivity
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class CollaborationTest(BpmnWorkflowTestCase):

    def testParseMessageFlow(self):

        spec, subprocesses = self.load_workflow_spec('collaboration.bpmn', 'process_buddy')
        self.assertDictEqual({'lover': ['lover_name']}, spec.correlation_keys)
        self.assertEqual(len(spec.outgoing_message_flows), 1)
        self.assertEqual(len(spec.incoming_message_flows), 1)
        outgoing, incoming = spec.outgoing_message_flows[0], spec.incoming_message_flows[0]

        self.assertEqual(outgoing.name, 'love_letter_flow')
        self.assertEqual(outgoing.message_ref, 'Love Letter')
        self.assertEqual(outgoing.source_process, 'process_buddy')
        self.assertEqual(outgoing.source_task, 'ActivitySendLetter')
        self.assertEqual(outgoing.target_process, 'random_person_process')
        self.assertEqual(outgoing.target_task, None)

        love_letter = spec.task_specs[outgoing.source_task].event_definition
        self.assertEqual(len(love_letter.correlation_properties), 1)
        prop = love_letter.correlation_properties[0]
        self.assertEqual(prop.name, 'lover_name')
        self.assertEqual(prop.expression, 'lover_name')
        self.assertListEqual(prop.correlation_keys, ['lover'])

        self.assertEqual(incoming.name, 'response_flow')
        self.assertEqual(incoming.message_ref, 'Love Letter Response')
        self.assertEqual(incoming.source_process, 'random_person_process')
        self.assertEqual(incoming.source_task, None)
        self.assertEqual(incoming.target_process, 'process_buddy')
        self.assertEqual(incoming.target_task, 'EventReceiveLetter')

        response = spec.task_specs[incoming.target_task].event_definition
        self.assertEqual(len(response.correlation_properties), 1)
        prop = response.correlation_properties[0]
        self.assertEqual(prop.name, 'lover_name')
        self.assertEqual(prop.expression, 'from_name')
        self.assertListEqual(prop.correlation_keys, ['lover'])

    def testCollaboration(self):

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

    def testBpmnMessage(self):

        spec, subprocesses = self.load_workflow_spec('collaboration.bpmn', 'process_buddy')
        workflow = BpmnWorkflow(spec, subprocesses)
        start = workflow.get_tasks_from_spec_name('Start')[0]
        # Set up some data to be evaluated so that the workflow can proceed
        start.data['lover_name'] = 'Peggy'
        workflow.do_engine_steps()
        # An external message should be created
        messages = workflow.get_bpmn_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(workflow.bpmn_messages), 0)
        receive = workflow.get_tasks_from_spec_name('EventReceiveLetter')[0]
        workflow.catch_bpmn_message('Love Letter Response', messages[0].payload, messages[0].correlations)
        workflow.do_engine_steps()
        # The external message created above should be caught
        self.assertEqual(receive.state, TaskState.COMPLETED)
        self.assertEqual(receive.data, messages[0].payload)
        self.assertEqual(workflow.is_completed(), True)

    def testCorrelation(self):

        specs = self.get_all_specs('correlation.bpmn')
        proc_1 = specs['proc_1']
        workflow = BpmnWorkflow(proc_1, specs)
        workflow.do_engine_steps()
        for idx, task in enumerate(workflow.get_ready_user_tasks()):
            task.data['task_num'] = idx
            task.complete()
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
        waiting = workflow.get_tasks_from_spec_name('get_response')
        # Two processes should have been started and two corresponding catch events should be waiting
        self.assertEqual(len(ready_tasks), 2)
        self.assertEqual(len(waiting), 2)
        for task in waiting:
            self.assertEqual(task.state, TaskState.WAITING)
        # Now copy the task_num that was sent into a new variable
        for task in ready_tasks:
            task.data.update(init_id=task.data['task_num'])
            task.complete()
        workflow.do_engine_steps()
        # If the messages were routed properly, the id should match
        for task in workflow.get_tasks_from_spec_name('subprocess_end'):
            self.assertEqual(task.data['task_num'], task.data['init_id'])

    def testSerialization(self):

        spec, subprocesses = self.load_collaboration('collaboration.bpmn', 'my_collaboration')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        start = self.workflow.get_tasks_from_spec_name('Start')[0]
        start.data['lover_name'] = 'Peggy'
        self.workflow.do_engine_steps()
        self.save_restore()