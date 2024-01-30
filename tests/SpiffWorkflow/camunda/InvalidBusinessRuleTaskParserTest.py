import unittest

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.exceptions import SpiffWorkflowException, WorkflowException

from .BaseTestCase import BaseTestCase


class BusinessRuleTaskParserTest(BaseTestCase):

    def setUp(self):
        self.spec, subproceses = self.load_workflow_spec(
            'invalid/InvalidDecision.bpmn', 'Process_1', 'invalid_decision.dmn')
        self.workflow = BpmnWorkflow(self.spec)

    def testExceptionPrint(self):
        e1 = Exception("test 1")
        e = SpiffWorkflowException("test")

    def testDmnRaisesTaskErrors(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_next_task(state=TaskState.READY).set_data(x=3)
        try:
            self.workflow.do_engine_steps()
            self.assertTrue(False, "An error should have been raised.")
        except WorkflowException as we:
            self.assertTrue(True, "An error was raised..")
            self.assertEqual("InvalidDecisionTaskId", we.task_spec.name)
            self.maxDiff = 1000
            self.assertEqual("Error evaluating expression 'spam= 1'. Rule failed on row 1. Business Rule Task 'Invalid Decision'.", str(we))
