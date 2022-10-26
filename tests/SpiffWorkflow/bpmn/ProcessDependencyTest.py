# -*- coding: utf-8 -*-
import os
import unittest

from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.spiff.parser import SpiffBpmnParser

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'danfunk'


class ProcessDependencyTest(BpmnWorkflowTestCase):
    """
    Assure we can determine all of the call activities and DMN references that
    will be required by a parser, prior to calling its parse method.

    Because DMN references vary between Camunda and Spiff, need to test that
    both methods will work.
    """

    def testCamundaParser(self):
        self.actual_test(CamundaParser())

    def testSpiffParser(self):
        self.actual_test(SpiffBpmnParser())

    def actual_test(self, parser):
        # We ought to test the parsers in the packages they belong to, not here.
        filename = 'call_activity_nested'
        process_name = 'Level1'
        base_dir = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser.add_bpmn_file(os.path.join(base_dir, 'call_activity_nested.bpmn'))
        dependencies = parser.get_dependencies()
        self.assertEqual(3, len(dependencies))
        process_deps = parser.get_process_dependencies()
        self.assertEqual(2, len(process_deps))
        self.assertIn('Level2', process_deps)
        self.assertIn('Level2b', process_deps)
        dmn_deps = parser.get_dmn_dependencies()
        self.assertEqual(1, len(dmn_deps))
        self.assertIn('Level2c', dmn_deps)

        # Add Level 2 file, and we should find a level 3 dependency as well.
        parser.add_bpmn_file(os.path.join(base_dir, 'call_activity_level_2.bpmn'))
        dependencies = parser.get_dependencies()
        self.assertEqual(4, len(dependencies))
        self.assertIn('Level3', dependencies)



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ProcessDependencyTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
