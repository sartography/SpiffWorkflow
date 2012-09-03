import unittest
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn2.workflow1 import WorkflowTest

__author__ = 'matth'


class MessagesTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Test Workflows')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()
        self.assertEquals([], self.workflow.get_tasks(Task.READY))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.accept_message('Wrong Message')
        self.assertEquals([], self.workflow.get_tasks(Task.READY))
        self.workflow.accept_message('Test Message')
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.assertEquals('Test Message', self.workflow.get_tasks(Task.READY)[0].task_spec.description)







def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ScriptsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())