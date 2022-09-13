# -*- coding: utf-8 -*-
import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class ServiceTaskTest(BpmnWorkflowTestCase):

    def setUp(self):

        spec, subprocesses = self.load_workflow_spec('service_task.bpmn', 
                'service_task_example1')
        self.workflow = BpmnWorkflow(spec, subprocesses) 

    def testRunThroughHappy(self):
        self.workflow.do_engine_steps()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ServiceTaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
