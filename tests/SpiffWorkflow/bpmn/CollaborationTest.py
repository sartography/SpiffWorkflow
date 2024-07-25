from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.mixins import CallActivityMixin

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

class CollaborationTest(BpmnWorkflowTestCase):

    def testParserProvidesInfoOnMessagesAndCorrelations(self):
        parser = self.get_parser('collaboration.bpmn')
        self.assertEqual(list(parser.messages.keys()), ['love_letter', 'love_letter_response'])
        self.assertEqual(parser.correlations,
                         {'lover_name': {'name': "Lover's Name",
                                         'retrieval_expressions': [
                                             {'expression': 'lover_name',
                                              'messageRef': 'love_letter'},
                                             {'expression': 'from_name',
                                              'messageRef': 'love_letter_response'}]}}
                         )

    def testCollaboration(self):

        spec, subprocesses = self.load_collaboration('collaboration.bpmn', 'my_collaboration')

        # Only executable processes should be started
        self.assertIn('process_buddy', subprocesses)
        self.assertNotIn('random_person_process', subprocesses)
        self.workflow = BpmnWorkflow(spec, subprocesses)
        start = self.workflow.task_tree
        # Set up some data to be evaluated so that the workflow can proceed
        start.data['lover_name'] = 'Peggy'
        self.workflow.do_engine_steps()

        # Call activities should be created for executable processes and be reachable
        buddy = self.workflow.get_next_task(spec_name='process_buddy')
        self.assertIsInstance(buddy.task_spec, CallActivityMixin)
        self.assertEqual(buddy.task_spec.spec, 'process_buddy')
        self.assertEqual(buddy.state, TaskState.STARTED)

    def testBpmnMessage(self):

        spec, subprocesses = self.load_workflow_spec('collaboration.bpmn', 'process_buddy')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        start = self.workflow.get_tasks(end_at_spec='Start')[0]
        # Set up some data to be evaluated so that the workflow can proceed
        start.data['lover_name'] = 'Peggy'
        self.workflow.do_engine_steps()
        # An external message should be created
        messages = self.workflow.get_events()
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(self.workflow.bpmn_events), 0)
        receive = self.workflow.get_next_task(spec_name='EventReceiveLetter')

        # Waiting Events should contain details about what we are no waiting on.
        events = self.workflow.waiting_events()
        self.assertEqual(1, len(events))
        self.assertEqual("MessageEventDefinition", events[0].event_type)
        self.assertEqual("Love Letter Response", events[0].name)
        self.assertEqual(['lover'], events[0].value[0].correlation_keys)
        self.assertEqual('from_name', events[0].value[0].retrieval_expression)
        self.assertEqual('lover_name', events[0].value[0].name)

        message = BpmnEvent(
            receive.task_spec.event_definition,
            {'from_name': 'Peggy', 'other_nonsense': 1001}
        )
        self.workflow.send_event(message)
        self.workflow.do_engine_steps()
        self.assertEqual(receive.state, TaskState.COMPLETED)
        self.assertEqual(self.workflow.last_task.data, {'from_name': 'Peggy', 'lover_name': 'Peggy', 'other_nonsense': 1001})
        self.assertEqual(self.workflow.correlations, {'lover':{'lover_name':'Peggy'}})
        self.assertEqual(self.workflow.completed, True)

    def testCorrelation(self):

        specs = self.get_all_specs('correlation.bpmn')
        proc_1 = specs['proc_1']
        self.workflow = BpmnWorkflow(proc_1, specs)
        self.workflow.do_engine_steps()
        for idx, task in enumerate(self.get_ready_user_tasks()):
            task.data['task_num'] = idx
            task.run()
        self.workflow.do_engine_steps()
        ready_tasks = self.get_ready_user_tasks()
        waiting = self.workflow.get_tasks(spec_name='get_response')
        # Two processes should have been started and two corresponding catch events should be waiting
        self.assertEqual(len(ready_tasks), 2)
        self.assertEqual(len(waiting), 2)
        for task in waiting:
            self.assertEqual(task.state, TaskState.WAITING)
        # Now copy the task_num that was sent into a new variable
        for task in ready_tasks:
            task.data.update(init_id=task.data['task_num'])
            task.run()
        self.workflow.do_engine_steps()
        # If the messages were routed properly, the id should match
        for task in self.workflow.get_next_task(spec_name='subprocess_end'):
            self.assertEqual(task.data['task_num'], task.data['init_id'])

    def testTwoCorrelationKeys(self):

        specs = self.get_all_specs('correlation_two_conversations.bpmn')
        proc_1 = specs['proc_1']
        self.workflow = BpmnWorkflow(proc_1, specs)
        self.workflow.do_engine_steps()
        for idx, task in enumerate(self.get_ready_user_tasks()):
            task.data['task_num'] = idx
            task.run()
        self.workflow.do_engine_steps()

        # Two processes should have been started and two corresponding catch events should be waiting
        ready_tasks = self.get_ready_user_tasks()
        waiting = self.workflow.get_tasks(spec_name='get_response_one')
        self.assertEqual(len(ready_tasks), 2)
        self.assertEqual(len(waiting), 2)
        for task in waiting:
            self.assertEqual(task.state, TaskState.WAITING)
        # Now copy the task_num that was sent into a new variable
        for task in ready_tasks:
            task.data.update(init_id=task.data['task_num'])
            task.run()
        self.workflow.do_engine_steps()

        # Complete dummy tasks
        for task in self.get_ready_user_tasks():
            task.run()
        self.workflow.do_engine_steps()

        # Repeat for the other process, using a different mapped name
        ready_tasks = self.get_ready_user_tasks()
        waiting = self.workflow.get_tasks(spec_name='get_response_two')
        self.assertEqual(len(ready_tasks), 2)
        self.assertEqual(len(waiting), 2)
        for task in ready_tasks:
            task.data.update(subprocess=task.data['task_num'])
            task.run()
        self.workflow.do_engine_steps()

        # If the messages were routed properly, the id should match
        for task in self.workflow.get_tasks(spec_name='subprocess_end'):
            self.assertEqual(task.data['task_num'], task.data['init_id'])
            self.assertEqual(task.data['task_num'], task.data['subprocess'])

    def testSerialization(self):

        spec, subprocesses = self.load_collaboration('collaboration.bpmn', 'my_collaboration')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        start = self.workflow.get_tasks(end_at_spec='Start')[0]
        start.data['lover_name'] = 'Peggy'
        self.workflow.do_engine_steps()
        self.save_restore()
