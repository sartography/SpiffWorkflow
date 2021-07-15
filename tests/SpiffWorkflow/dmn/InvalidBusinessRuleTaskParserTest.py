import os
import unittest

from SpiffWorkflow.exceptions import WorkflowTaskExecException

from SpiffWorkflow import Task, WorkflowException

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class BusinessRuleTaskParserTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def setUp(self):
        parser = BpmnDmnParser()
        bpmn = os.path.join(os.path.dirname(__file__), 'data', 'InvalidBpmnDmn',
                            'InvalidDecision.bpmn')
        dmn = os.path.join(os.path.dirname(__file__), 'data', 'InvalidBpmnDmn',
                            'invalid_decision.dmn')
        parser.add_bpmn_file(bpmn)
        parser.add_dmn_file(dmn)
        self.spec = parser.get_spec('Process_1')
        self.workflow = BpmnWorkflow(self.spec)

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnRaisesTaskErrors(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(Task.READY)[0].set_data(x=3)
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
