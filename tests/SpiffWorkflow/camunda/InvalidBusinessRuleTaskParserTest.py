import os
import unittest

from SpiffWorkflow.exceptions import SpiffWorkflowException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase


class BusinessRuleTaskParserTest(BaseTestCase):

    def setUp(self):
        self.spec, subproceses = self.load_workflow_spec(
            'invalid/InvalidDecision.bpmn', 'Process_1', 'invalid_decision.dmn')
        self.workflow = BpmnWorkflow(self.spec)

    def testExceptionPrint(self):
        e1 = Exception("test 1")
        print (e1)
        e = SpiffWorkflowException("test")
        print (e)

    def testDmnRaisesTaskErrors(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(TaskState.READY)[0].set_data(x=3)
        try:
            self.workflow.do_engine_steps()
            self.assertTrue(False, "An error should have been raised.")
        except SpiffWorkflowException as we:
            self.assertTrue(True, "An error was raised..")
            self.assertEqual("InvalidDecisionTaskId", we.sender.name)
            self.maxDiff  = 1000
            self.assertEquals("Error evaluating expression 'spam= 1'. Rule failed on row 1. Business Rule Task 'Invalid Decision'.", str(we))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BusinessRuleTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
