import os
import unittest

from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase


class BusinessRuleTaskParserTest(BaseTestCase):

    def setUp(self):
        self.spec, subproceses = self.load_workflow_spec(
            'invalid/InvalidDecision.bpmn', 'Process_1', 'invalid_decision.dmn')
        self.workflow = BpmnWorkflow(self.spec)

    def testDmnRaisesTaskErrors(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(TaskState.READY)[0].set_data(x=3)
        try:
            self.workflow.do_engine_steps()
            self.assertTrue(False, "An error should have been raised.")
        except WorkflowTaskExecException as we:
            self.assertTrue(True, "An error was raised..")
            self.assertEquals("InvalidDecisionTaskId", we.sender.name)
            self.maxDiff  = 1000
            self.assertEquals("InvalidDecisionTaskId: Failed to execute "
                              "expression: 'spam' is '= 1' in the Row with "
                              "annotation 'This is complletely wrong.'"
                              ", invalid syntax (<string>, line 1)",
                              str(we))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BusinessRuleTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
