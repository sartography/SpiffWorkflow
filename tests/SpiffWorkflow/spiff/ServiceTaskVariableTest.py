# -*- coding: utf-8 -*-
import json
import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from .BaseTestCase import BaseTestCase

class ServiceTaskDelegate:
    @staticmethod
    def call_connector(name, params, task_data):
        assertEqual(name, 'bamboohr/GetPayRate')
        assertEqual(len(params), 3)
        assertEqual(params['api_key']['value'], 'secret:BAMBOOHR_API_KEY')
        assertEqual(params['employee_id']['value'], '109')
        assertEqual(params['subdomain']['value'], 'statusdemo')

        sample_response = {
            "amount": "65000.00",
            "currency": "USD",
            "id": "4",
            "payRate": "65000.00 USD",
        }

        return json.dumps(sample_response)

class ExampleCustomScriptEngine(PythonScriptEngine):
    def call_service(self, operation_name, operation_params, task_data):
        return ServiceTaskDelegate.call_connector(operation_name, operation_params,
                task_data)

class ServiceTaskVariableTest(BaseTestCase):

    def setUp(self):
        global assertEqual
        assertEqual = self.assertEqual

        spec, subprocesses = self.load_workflow_spec('service_task_variable.bpmn',
                'Process_bd2e724555')
        self.script_engine = ExampleCustomScriptEngine()
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.workflow.do_engine_steps()
        self._assert_service_task()

    def testRunThroughSaveRestore(self):
        self.save_restore()
        # Engine isn't preserved through save/restore, so we have to reset it.
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.save_restore()
        self._assert_service_task()

    def _assert_service_task(self):
        result = self.workflow.data['spiff__Activity_0xhr131_result']
        self.assertEqual(len(result), 4)
        self.assertEqual(result['amount'], '65000.00')
        self.assertEqual(result['currency'], 'USD')
        self.assertEqual(result['id'], '4')
        self.assertEqual(result['payRate'], '65000.00 USD')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ServiceTaskVariableTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
