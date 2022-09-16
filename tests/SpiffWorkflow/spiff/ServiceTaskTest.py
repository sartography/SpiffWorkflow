# -*- coding: utf-8 -*-
import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from .BaseTestCase import BaseTestCase

# TODO must be a better way to do this
assertEqual = None
operatorExecuted = False

class ServiceTaskDelegate:
    @staticmethod
    def call_connector(name, params):
        assertEqual(name, 'bamboohr/GetPayRate')
        assertEqual(len(params), 3)
        assertEqual(params['api_key']['value'], 'secret:BAMBOOHR_API_KEY')
        assertEqual(params['employee_id']['value'], '4')
        assertEqual(params['subdomain']['value'], 'ServiceTask')

        global operatorExecuted
        operatorExecuted = True

class ExampleCustomScriptEngine(PythonScriptEngine):
    def available_service_task_external_methods(self):
        return { 'ServiceTaskDelegate': ServiceTaskDelegate }

class ServiceTaskTest(BaseTestCase):

    def setUp(self):
        global assertEqual, operatorExecuted
        assertEqual = self.assertEqual
        operatorExecuted = False

        spec, subprocesses = self.load_workflow_spec('service_task.bpmn',
                'service_task_example1')
        self.script_engine = ExampleCustomScriptEngine()
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.workflow.do_engine_steps()
        self.assertTrue(operatorExecuted)

    def testRunThroughSaveRestore(self):
        self.save_restore()
        # Engine isn't preserved through save/restore, so we have to reset it.
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertTrue(operatorExecuted)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ServiceTaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
