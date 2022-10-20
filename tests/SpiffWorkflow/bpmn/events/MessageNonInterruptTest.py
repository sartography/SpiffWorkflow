# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageNonInterruptTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Test Workflows', False)

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.catch(MessageEventDefinition('Test Message'))
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Do Something That Takes A Long Time')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageInterrupt(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.catch(MessageEventDefinition('Test Message'))

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_named_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageInterruptOtherOrder(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.catch(MessageEventDefinition('Test Message'))

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageInterruptOtherOrderSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step(
            'Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.catch(MessageEventDefinition('Test Message'))
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessageNonInterruptTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
