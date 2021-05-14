# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow.bpmn.BpmnScriptEngine import BpmnScriptEngine
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class SubWorkflowMultiTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        # for now we are testing the completion condition
        # There is also a test bpmn sub_workflow_multi.bpmn that tests the exact same
        # thing, except for the script is in a call activity. This is currently not working the way
        # we want it to, but it should
        return self.load_workflow_spec('sub_workflow_multi1.bpmn', 'ScriptTest')

    def testRunThroughHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        data = self.workflow.last_task.data

        self.assertEqual(data['coll'], {1: {'a': 1}, 2: {'a': 2}, 3: {'a': 3}})





def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SubWorkflowMultiTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
