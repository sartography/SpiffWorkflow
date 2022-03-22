# -*- coding: utf-8 -*-



import unittest
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessagesTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Test Workflows')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()
        self.assertEqual([], self.workflow.get_tasks(Task.READY))
        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.message('Wrong Message')
        self.assertEqual([], self.workflow.get_tasks(Task.READY))
        self.workflow.message('Test Message')
        self.assertEqual(1, len(self.workflow.get_tasks(Task.READY)))

        self.assertEqual(
            'Test Message', self.workflow.get_tasks(Task.READY)[0].task_spec.description)

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()

        self.save_restore()

        self.assertEqual([], self.workflow.get_tasks(Task.READY))
        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.message('Wrong Message')
        self.assertEqual([], self.workflow.get_tasks(Task.READY))
        self.workflow.message('Test Message')

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessagesTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
