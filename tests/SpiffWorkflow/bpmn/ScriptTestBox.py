# -*- coding: utf-8 -*-



import unittest
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class InlineScriptTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('ScriptTestBox.bpmn', 'ScriptTest')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        data = self.workflow.last_task.data
        self.assertEqual(data,{'testvar': {'a': 1, 'b': 2, 'new': 'Test'},
                               'testvar2': [{'x': 1, 'y': 'a'},
                                            {'x': 2, 'y': 'b'},
                                            {'x': 3, 'y': 'c'}],
                               'sample': ['b', 'c'], 'end_event': None})




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InlineScriptTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
