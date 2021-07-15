import os
import unittest

from SpiffWorkflow.exceptions import WorkflowTaskExecException

from SpiffWorkflow import Task, WorkflowException

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class InvalidBusinessRuleNameErrorTest(unittest.TestCase):

    def test_integer_decision_string_output_inclusive(self):
        runner = DecisionRunner('invalid_decision_name_error.dmn',
                                debug='DEBUG')
        try:
            res = runner.decide({'spam': 1})
        except Exception as e:
            self.assertRegexpMatches(str(e), "did you mean one of \['spam'\]")

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidBusinessRuleNameErrorTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
