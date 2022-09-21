# -*- coding: utf-8 -*-



import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'leashys'


class ParallelWithScriptTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('ParallelWithScript.bpmn', 'ParallelWithScript')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughParallel(self):
        self.workflow.do_engine_steps()
        # TODO: what to assert here?

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParallelWithScriptTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
