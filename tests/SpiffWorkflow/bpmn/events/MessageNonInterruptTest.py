from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.event import BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions.message import MessageEventDefinition
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageNonInterruptTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec(
            'Test-Workflows/*.bpmn20.xml',
            'sid-b0903a88-fe74-4f93-b912-47b815ea8d1c', 
            False)

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughMessageInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Do Something That Takes A Long Time')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughMessageInterrupt(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))

        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(3, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.do_next_named_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughMessageInterruptOtherOrder(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))

        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughMessageInterruptOtherOrderSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))
