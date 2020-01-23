import os
import unittest

from SpiffWorkflow import Task

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class BusinessRuleTaskParserTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def setUp(self):
        parser = BpmnDmnParser()
        bpmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'ExclusiveGatewayIfElseAndDecision.bpmn')
        dmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'test_integer_decision.dmn')
        parser.add_bpmn_file(bpmn)
        parser.add_dmn_file(dmn)
        self.spec = parser.get_spec('Process_1')
        self.workflow = BpmnWorkflow(self.spec)

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(Task.READY)[0].set_data(x=3)
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.data, {'x': 3, 'y': 'A'})

    def testDmnSaveRestore(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(Task.READY)[0].set_data(x=3)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertDictEqual(self.workflow.data, {'x': 3, 'y': 'A'})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BusinessRuleTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
