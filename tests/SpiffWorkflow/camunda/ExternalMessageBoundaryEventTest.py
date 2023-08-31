from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.event import BpmnEvent
from SpiffWorkflow.camunda.specs.event_definitions import MessageEventDefinition
from .BaseTestCase import BaseTestCase

__author__ = 'kellym'


class ExternalMessageBoundaryTest(BaseTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('external_message.bpmn', 'Process_1iggtmi')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):

        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(1, len(ready_tasks),'Expected to have only one ready task')
        self.workflow.catch(BpmnEvent(
            MessageEventDefinition('Interrupt'),
            {'result_var': 'interrupt_var', 'payload': 'SomethingImportant'}
        ))
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(2,len(ready_tasks),'Expected to have two ready tasks')

        # item 1 should be at 'Pause'
        self.assertEqual('Pause',ready_tasks[1].task_spec.bpmn_name)
        self.assertEqual('SomethingImportant', ready_tasks[1].data['interrupt_var'])
        self.assertEqual(True, ready_tasks[1].data['caughtinterrupt'])
        self.assertEqual('Meaningless User Task',ready_tasks[0].task_spec.bpmn_name)
        self.assertEqual(False, ready_tasks[0].data['caughtinterrupt'])
        ready_tasks[1].run()
        self.workflow.do_engine_steps()

        self.workflow.catch(BpmnEvent(
            MessageEventDefinition('reset'),
            {'result_var': 'reset_var', 'payload': 'SomethingDrastic'}
        ))
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        # The user activity was cancelled and we should continue from the boundary event
        self.assertEqual(2, len(ready_tasks), 'Expected to have two ready tasks')
        event = self.workflow.get_next_task(spec_name='Event_19detfv')
        event.run()
        self.assertEqual('SomethingDrastic', event.data['reset_var'])
        self.assertEqual(False, event.data['caughtinterrupt'])
