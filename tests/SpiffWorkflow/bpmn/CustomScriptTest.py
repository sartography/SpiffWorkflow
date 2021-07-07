# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow.bpmn.BpmnScriptEngine import BpmnScriptEngine
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

def my_custom_function(txt):
    return str(txt).upper()

class CustomBpmnScriptEngine(BpmnScriptEngine):
    """This is a custom script processor that can be easily injected into Spiff Workflow.
    It will execute python code read in from the bpmn.  It will also make any scripts in the
     scripts directory available for execution. """


    def execute(self, task, script, data):
        augmentMethods = {'custom_function': my_custom_function}
        super().execute(task, script, data, external_methods=augmentMethods)
    def eval(self, exp, data):
        return super()._eval(exp, {}, **data)




class CustomInlineScriptTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('custom_function_test.bpmn', 'ScriptTest')

    def testRunThroughHappy(self):
        script_engine = CustomBpmnScriptEngine()
        self.workflow = BpmnWorkflow(self.spec,script_engine=script_engine)
        self.workflow.do_engine_steps()
        data = self.workflow.last_task.data
        self.assertEqual(data['c1'], 'HELLO')
        self.assertEqual(data['c2'], 'GOODBYE')




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CustomInlineScriptTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
