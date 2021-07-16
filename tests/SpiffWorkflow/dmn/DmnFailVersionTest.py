import os
import unittest

from SpiffWorkflow import Task

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class DmnVersionTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def setUp(self):
        self.parser = BpmnDmnParser()

    def testLoad(self):
        dmn = os.path.join(os.path.dirname(__file__), 'data',
                            'dmn_version_fail_test.dmn')
        with self.assertRaises(IndexError):
            self.parser.add_dmn_file(dmn)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DmnVersionTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
